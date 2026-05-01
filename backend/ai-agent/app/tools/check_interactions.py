
import json
import httpx
from itertools import combinations
from app.services.llm_service import call_llm
from app.utils.parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger("check_interactions")

# Correct RxNorm endpoints
RXCUI_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
INTERACTION_URL = "https://rxnav.nlm.nih.gov/REST/interaction/interaction.json"
INTERACTION_LIST_URL = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"


def _get_rxcui(drug_name: str) -> str | None:
    """Resolve drug name to a single RxCUI."""
    try:
        r = httpx.get(
            RXCUI_URL,
            params={"name": drug_name, "search": "1"},
            timeout=10,
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        ids = r.json().get("idGroup", {}).get("rxnormId", [])
        cui = ids[0] if ids else None
        logger.debug(f"RxCUI for {drug_name}: {cui}")
        return cui
    except Exception as e:
        logger.warning(f"RxCUI lookup failed for {drug_name}: {e}")
        return None


def _check_rxnorm_list(rxcuis: list[str]) -> list[dict]:
    """
    Use the /interaction/list.json endpoint which accepts multiple RxCUIs.
    This is the correct bulk endpoint.
    """
    try:
        # Build query string manually — this endpoint needs rxcuis as repeated params
        params = "&".join([f"rxcuis={c}" for c in rxcuis])
        url = f"{INTERACTION_LIST_URL}?{params}"
        logger.debug(f"Calling RxNorm list endpoint: {url}")

        r = httpx.get(url, timeout=15, headers={"Accept": "application/json"})
        logger.debug(f"RxNorm response status: {r.status_code}, length: {len(r.text)}")

        if r.status_code != 200 or not r.text.strip():
            logger.warning(f"RxNorm returned empty or non-200: {r.status_code}")
            return []

        data = r.json()
        results = []

        for group in data.get("fullInteractionTypeGroup", []):
            source = group.get("sourceName", "")
            for itype in group.get("fullInteractionType", []):
                for pair in itype.get("interactionPair", []):
                    concepts = pair.get("interactionConcept", [])
                    drug_names = [
                        c.get("minConceptItem", {}).get("name", "")
                        for c in concepts
                    ]
                    results.append({
                        "drugs": drug_names,
                        "severity": pair.get("severity", "unknown"),
                        "description": pair.get("description", ""),
                        "source": source,
                    })

        logger.info(f"RxNorm found {len(results)} interactions")
        return results

    except Exception as e:
        logger.warning(f"RxNorm list endpoint failed: {e}")
        return []


def _check_rxnorm_single(cui: str, drug_name: str) -> list[dict]:
    """
    Fallback: check interactions for a single drug using /interaction/interaction.json
    """
    try:
        r = httpx.get(
            INTERACTION_URL,
            params={"rxcui": cui},
            timeout=10,
            headers={"Accept": "application/json"},
        )
        logger.debug(f"Single drug check for {drug_name} ({cui}): status {r.status_code}, len {len(r.text)}")

        if r.status_code != 200 or not r.text.strip():
            return []

        data = r.json()
        results = []
        for group in data.get("interactionTypeGroup", []):
            for itype in group.get("interactionType", []):
                for pair in itype.get("interactionPair", []):
                    concepts = pair.get("interactionConcept", [])
                    drug_names = [
                        c.get("minConceptItem", {}).get("name", "")
                        for c in concepts
                    ]
                    results.append({
                        "drugs": drug_names,
                        "severity": pair.get("severity", "unknown"),
                        "description": pair.get("description", ""),
                    })
        return results
    except Exception as e:
        logger.warning(f"Single drug RxNorm check failed for {drug_name}: {e}")
        return []


def _check_llm(medications: list[dict]) -> dict:
    """LLM-based interaction check as final fallback."""
    logger.info("Using LLM for drug interaction check")
    med_list = ", ".join([
        f"{m.get('name','?')} {m.get('dose','')}".strip()
        for m in medications
    ])

    prompt = f"""You are a clinical pharmacology expert.

Analyze these medications for drug-drug interactions: {med_list}

Return ONLY this JSON structure, no other text:
{{
  "source": "llm",
  "interactions_found": true,
  "details": [
    {{
      "drugs": ["drug1", "drug2"],
      "severity": "mild|moderate|severe",
      "description": "specific clinical description of the interaction"
    }}
  ],
  "overall_safety": "safe|caution|unsafe",
  "recommendation": "specific recommendation for prescribing doctor"
}}

If no interactions exist, set interactions_found to false and details to [].
Be specific and clinically accurate."""

    try:
        raw = call_llm(
            prompt,
            system="You are a clinical pharmacology AI. Return only valid JSON with no markdown.",
        )
        result = parse_json_response(raw)
        result["source"] = "llm"
        logger.info(f"LLM check complete. Interactions found: {result.get('interactions_found')}")
        return result
    except Exception as e:
        logger.error(f"LLM interaction check failed: {e}")
        return {
            "source": "llm",
            "interactions_found": False,
            "details": [],
            "error": str(e),
        }


def run(medications: list[dict]) -> dict:
    logger.info(f"Checking interactions for {len(medications)} medications")

    if not medications:
        logger.warning("No medications provided")
        return {"interactions_found": False, "details": [], "message": "No medications provided."}

    # Step 1: Resolve all RxCUIs
    drug_cui_map = {}
    for med in medications:
        name = med.get("name", "").strip()
        if name:
            drug_cui_map[name] = _get_rxcui(name)

    logger.debug(f"Drug CUI map: {drug_cui_map}")
    valid_cuis = {k: v for k, v in drug_cui_map.items() if v}

    # Step 2: Try bulk RxNorm list endpoint
    if len(valid_cuis) >= 2:
        cui_list = list(valid_cuis.values())
        api_details = _check_rxnorm_list(cui_list)

        # Step 3: If bulk fails, try single-drug endpoint for each
        if not api_details:
            logger.info("Bulk RxNorm failed, trying single-drug endpoints")
            for name, cui in valid_cuis.items():
                single = _check_rxnorm_single(cui, name)
                api_details.extend(single)

        if api_details:
            logger.info(f"RxNorm API succeeded with {len(api_details)} interactions")
            # Also run LLM to supplement
            llm_result = _check_llm(medications)
            all_details = api_details + llm_result.get("details", [])
            return {
                "source": "rxnorm+llm",
                "interactions_found": True,
                "details": all_details,
                "overall_safety": llm_result.get("overall_safety", "caution"),
                "recommendation": llm_result.get("recommendation", ""),
                "api_attempted": True,
            }
        else:
            logger.warning("All RxNorm endpoints returned empty — falling back to LLM only")

    # Step 4: LLM-only fallback
    result = _check_llm(medications)
    result["api_attempted"] = bool(valid_cuis)
    return result
