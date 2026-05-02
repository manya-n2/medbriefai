"""
check_interactions v6
- USE_RXNORM = False bypasses slow RxNorm API (toggle to True to re-enable)
- All RxNorm code preserved — just skipped when flag is False
- LLM fallback unchanged
- _overall_assessment rule-based (no LLM call)
"""

import httpx
from app.services.llm_service import call_llm
from app.agent.memory import load_prompt
from app.utils.parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger("check_interactions")

# ── Toggle this to True if RxNorm becomes available in your environment ──
USE_RXNORM = False

RXCUI_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
INTERACTION_URL = "https://rxnav.nlm.nih.gov/REST/interaction/interaction.json"

SEVERITY_ORDER = {"critical": 0, "severe": 1, "high": 2, "moderate": 3, "mild": 4, "minor": 5, "unknown": 6}
VALID_SEVERITIES = {"critical", "severe", "high", "moderate", "mild", "minor"}

FALSE_POSITIVE_PAIRS = {
    frozenset(["ramipril", "atorvastatin"]),
    frozenset(["atorvastatin", "metoprolol"]),
    frozenset(["aspirin", "atorvastatin"]),
    frozenset(["metformin", "aspirin"]),
    frozenset(["ramipril", "metoprolol"]),
    frozenset(["nitroglycerin", "atorvastatin"]),
    frozenset(["clopidogrel", "atorvastatin"]),
}

EXPECTED_THERAPY = {
    frozenset(["aspirin", "clopidogrel"]): "Dual antiplatelet therapy — expected in ACS. Add PPI to reduce GI bleed risk.",
    frozenset(["aspirin", "warfarin"]): "Combined antithrombotic — intentional but high bleeding risk. Monitor INR closely.",
    frozenset(["metformin", "ramipril"]): "Common in diabetic hypertension — beneficial combination. Monitor renal function.",
}


# ── RxNorm (preserved, bypassed when USE_RXNORM = False) ──────────────────

def _get_rxcui(drug_name: str) -> str | None:
    try:
        r = httpx.get(
            RXCUI_URL,
            params={"name": drug_name, "search": "1"},
            timeout=2.0,
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200 and r.text.strip():
            ids = r.json().get("idGroup", {}).get("rxnormId", [])
            return ids[0] if ids else None
        return None
    except Exception:
        return None


def _rxnorm_check(medications: list[dict]) -> list[dict] | None:
    med_names_lower = {m.get("name", "").lower() for m in medications}
    drug_cui_map = {}
    for med in medications:
        name = med.get("name", "").strip()
        if name:
            cui = _get_rxcui(name)
            if cui:
                drug_cui_map[name] = cui

    if not drug_cui_map:
        logger.info("RxNorm: CUI resolution failed — API likely blocked, skipping to LLM")
        return None

    results = []
    api_responded = False

    for drug_name, cui in drug_cui_map.items():
        try:
            r = httpx.get(
                INTERACTION_URL,
                params={"rxcui": cui},
                timeout=3.0,
                headers={"Accept": "application/json"},
            )
            if r.status_code != 200 or not r.text.strip() or len(r.text) < 10:
                continue
            api_responded = True
            data = r.json()
            for group in data.get("interactionTypeGroup", []):
                source = group.get("sourceName", "RxNorm")
                for itype in group.get("interactionType", []):
                    for pair in itype.get("interactionPair", []):
                        concepts = pair.get("interactionConcept", [])
                        drug_names = [c.get("minConceptItem", {}).get("name", "") for c in concepts]
                        pair_lower = frozenset(d.lower() for d in drug_names)
                        if not pair_lower.issubset(med_names_lower):
                            continue
                        if pair_lower in FALSE_POSITIVE_PAIRS:
                            continue
                        sev = _normalize_severity(pair.get("severity", "unknown"))
                        is_expected = pair_lower in EXPECTED_THERAPY
                        results.append({
                            "drugs": drug_names,
                            "severity": sev,
                            "description": pair.get("description", ""),
                            "source": f"rxnorm:{source}",
                            "confidence": 0.93,
                            "clinical_context": "expected_therapy" if is_expected else "monitor_closely",
                            "is_expected_therapy": is_expected,
                            "recommendation": EXPECTED_THERAPY.get(pair_lower, _default_recommendation(sev)),
                        })
        except Exception as e:
            logger.warning(f"RxNorm query failed for {drug_name}: {e}")

    return results if api_responded else None


# ── Structured LLM fallback ────────────────────────────────────────────────

def _structured_llm_check(medications: list[dict]) -> list[dict]:
    med_names = [m.get("name", "").strip() for m in medications if m.get("name")]
    med_names_lower_set = {n.lower() for n in med_names}
    med_list_str = ", ".join(med_names)

    try:
        prompt_template = load_prompt("interactions")
        prompt = prompt_template.replace("{med_list}", med_list_str)
    except FileNotFoundError:
        logger.error("interactions.txt prompt not found!")
        return []

    try:
        raw = call_llm(
            prompt,
            system="Clinical pharmacologist. Return only a valid JSON array. Use only the exact drug names provided. No markdown.",
            temperature=0.0      # ← was 0.05
                    # ← added
        )
        logger.debug(f"LLM interaction raw: {raw[:300]}")
        raw_parsed = parse_json_response(raw)

        if not isinstance(raw_parsed, list):
            logger.error(f"LLM returned non-list type: {type(raw_parsed)}")
            return []

    except Exception as e:
        logger.error(f"LLM call or parse failed: {e}")
        return []

    validated = []
    seen_pairs = set()

    for item in raw_parsed:
        if not isinstance(item, dict):
            continue
        drugs = item.get("drugs", [])
        if not isinstance(drugs, list) or len(drugs) != 2:
            continue
        drugs_lower = frozenset(d.lower() for d in drugs)
        if not drugs_lower.issubset(med_names_lower_set):
            continue
        if drugs_lower in FALSE_POSITIVE_PAIRS:
            continue
        if drugs_lower in seen_pairs:
            continue
        seen_pairs.add(drugs_lower)

        severity = str(item.get("severity", "moderate")).lower().strip()
        if severity not in VALID_SEVERITIES:
            severity = "moderate"

        mechanism = str(item.get("mechanism", "")).strip()
        clinical  = str(item.get("clinical_significance", "")).strip()
        if mechanism and clinical:
            description = f"{mechanism} — {clinical}"
        elif mechanism:
            description = mechanism
        elif clinical:
            description = clinical
        else:
            description = "Drug interaction detected."

        is_expected = drugs_lower in EXPECTED_THERAPY
        clinical_context = "expected_therapy" if is_expected else (
            "dangerous" if severity in ("critical", "severe") else "monitor_closely"
        )

        validated.append({
            "drugs": drugs,
            "severity": severity,
            "description": description,
            "source": "llm_structured",
            "confidence": 0.78,
            "clinical_context": clinical_context,
            "is_expected_therapy": is_expected,
            "recommendation": str(item.get("recommendation", "")).strip() or _default_recommendation(severity),
        })

    logger.info(f"LLM structured: {len(raw_parsed)} raw → {len(validated)} validated")
    return validated


# ── Overall assessment — rule-based only (no LLM call) ────────────────────

def _overall_assessment(interactions: list[dict], medications: list[dict]) -> dict:
    if not interactions:
        return {
            "overall_safety": "safe",
            "recommendation": "No clinically significant interactions detected. Continue with standard monitoring.",
        }

    severities = [
        i.get("severity", "unknown")
        for i in interactions
        if not i.get("is_expected_therapy")
    ]

    if "critical" in severities or "severe" in severities:
        overall_safety = "unsafe"
        recommendation = (
            "⚠️ Severe interaction detected. Do not dispense without specialist review. "
            "Consider alternative therapy immediately."
        )
    elif "moderate" in severities:
        overall_safety = "caution"
        top = next(
            (i for i in interactions
             if i.get("severity") == "moderate" and not i.get("is_expected_therapy")),
            None,
        )
        recommendation = (
            top.get("recommendation")
            if top and top.get("recommendation")
            else "Moderate interactions present. Monitor closely and consider alternatives if clinically feasible."
        )
    elif any(i.get("is_expected_therapy") for i in interactions):
        overall_safety = "caution"
        recommendation = (
            "Medications include expected therapeutic combinations. "
            "Ensure appropriate monitoring protocols are in place."
        )
    else:
        overall_safety = "caution"
        recommendation = "Mild interactions noted. Routine monitoring recommended."

    return {"overall_safety": overall_safety, "recommendation": recommendation}


# ── Helpers ────────────────────────────────────────────────────────────────

def _normalize_severity(raw: str) -> str:
    mapping = {
        "contraindicated": "critical",
        "major": "severe",
        "serious": "severe",
        "significant": "moderate",
        "minor": "mild",
        "low": "mild",
        "minimal": "mild",
    }
    raw = raw.lower().strip()
    return mapping.get(raw, raw if raw in VALID_SEVERITIES else "moderate")


def _default_recommendation(severity: str) -> str:
    if severity in ("critical", "severe"):
        return "Avoid combination unless absolutely necessary. Consult specialist immediately."
    if severity == "moderate":
        return "Monitor closely. Consider alternatives if clinically feasible."
    return "Standard monitoring recommended."


# ── Main entry ─────────────────────────────────────────────────────────────

def run(medications: list[dict]) -> dict:
    logger.info(f"Checking interactions for {len(medications)} medications")

    if not medications:
        return {"interactions_found": False, "details": [], "source": "none",
                "message": "No medications provided."}
    if len(medications) < 2:
        return {"interactions_found": False, "details": [], "source": "none",
                "message": "At least 2 medications required."}

    # ── USE_RXNORM flag: set False to skip slow API entirely ──────────────
    rxnorm_results = None if not USE_RXNORM else _rxnorm_check(medications)
    source = "rxnorm"

    if rxnorm_results is None:
        logger.info("RxNorm skipped or unavailable — using structured LLM")
        interactions = _structured_llm_check(medications)
        source = "llm_structured"
    elif not rxnorm_results:
        logger.info("RxNorm returned 0 — supplementing with structured LLM")
        interactions = _structured_llm_check(medications)
        source = "llm_structured"
    else:
        interactions = rxnorm_results

    seen = set()
    deduped = []
    for item in interactions:
        pair = frozenset(d.lower() for d in item.get("drugs", []))
        if pair not in seen:
            seen.add(pair)
            deduped.append(item)

    deduped.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "unknown"), 6))
    top = deduped[:5]

    assessment = _overall_assessment(top, medications)

    logger.info(f"Final: {len(top)} interactions | source={source} | safety={assessment['overall_safety']}")

    return {
        "interactions_found": len(top) > 0,
        "details": top,
        "overall_safety": assessment["overall_safety"],
        "recommendation": assessment["recommendation"],
        "source": source,
        "api_attempted": USE_RXNORM,
        "rxnorm_available": rxnorm_results is not None,
        "total_checked": len(medications),
    }