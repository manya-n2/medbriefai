import json
from app.services.llm_service import call_llm
from app.agent.memory import load_prompt
from app.utils.parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger("detect_risks")


# ─────────────────────────────────────────────
#  HELPERS  (unchanged)
# ─────────────────────────────────────────────

def _to_float(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = str(val).replace("%", "").replace("°F", "").replace("°C", "").replace("bpm", "").replace("breaths/min", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_bp(bp_val) -> tuple[int, int]:
    if not bp_val:
        return (0, 0)
    bp_str = str(bp_val).replace("mmHg", "").strip()
    if "/" in bp_str:
        parts = bp_str.split("/")
        try:
            return (int(float(parts[0].strip())), int(float(parts[1].strip())))
        except (ValueError, IndexError):
            return (0, 0)
    return (0, 0)


def _is_normal_vitals(vitals: dict) -> bool:
    systolic, diastolic = _parse_bp(vitals.get("bp"))
    pulse = _to_float(vitals.get("pulse"))
    temp  = _to_float(vitals.get("temp"))
    spo2  = _to_float(vitals.get("spo2"))

    logger.debug(f"Vitals parsed → systolic={systolic} diastolic={diastolic} pulse={pulse} temp={temp} spo2={spo2}")

    bp_ok    = 0 < systolic <= 139 and 0 < diastolic <= 89
    pulse_ok = 0 < pulse < 100
    temp_ok  = 0 < temp <= 99.5
    spo2_ok  = 0 < spo2 >= 95

    if systolic == 0: bp_ok    = True
    if pulse == 0:    pulse_ok = True
    if temp == 0:     temp_ok  = True
    if spo2 == 0:     spo2_ok  = True

    result = bp_ok and pulse_ok and temp_ok and spo2_ok
    logger.debug(f"is_normal_vitals → {result} (bp={bp_ok} pulse={pulse_ok} temp={temp_ok} spo2={spo2_ok})")
    return result


def _is_mild_symptoms(symptoms: list) -> bool:
    if not symptoms or len(symptoms) > 3:
        return False
    mild_keywords    = ["mild", "slight", "minor", "light", "tension headache", "fatigue", "headache"]
    severe_keywords  = ["severe", "acute", "chest pain", "shortness of breath", "dyspnea",
                        "syncope", "collapse", "unconscious", "vomiting blood", "seizure",
                        "stroke", "paralysis", "crushing"]
    has_severe = any(any(kw in s.lower() for kw in severe_keywords) for s in symptoms)
    if has_severe:
        return False
    return any(any(kw in s.lower() for kw in mild_keywords) for s in symptoms)


def _score_for_level(level: str) -> int:
    return {"critical": 90, "high": 75, "moderate": 50, "low": 20}.get(level.lower(), 50)


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def run(extracted_data: dict, interaction_results: dict) -> dict:
    logger.info("Starting risk detection")

    try:
        vitals   = extracted_data.get("vitals", {}) or {}
        symptoms = extracted_data.get("symptoms", []) or []

        # ── Rule-based guard: skip LLM entirely for clear low-risk ──────
        if _is_normal_vitals(vitals) and _is_mild_symptoms(symptoms):
            logger.info("Rule-based LOW risk applied — skipping LLM")
            return {
                "risk_level": "low",
                "score": 20,
                "risks": [{
                    "type": "symptom",
                    "description": "Mild symptoms with all vitals within normal limits",
                    "severity": "low",
                    "confidence": 0.95
                }],
                "immediate_action_required": False,
                "summary": "Low-risk patient with stable vitals; routine outpatient care is sufficient."
            }

        # ── Minimal payload: strip notes/allergies/medications to reduce tokens ──
        minimal_data = {
            "age":       extracted_data.get("age"),
            "gender":    extracted_data.get("gender"),
            "symptoms":  symptoms,
            "vitals":    vitals,
            "diagnosis": extracted_data.get("diagnosis"),
        }

        # Minimal interaction summary: only severity + drug names, no descriptions
        minimal_interactions = {
            "interactions_found": interaction_results.get("interactions_found", False),
            "overall_safety":     interaction_results.get("overall_safety", "safe"),
            "details": [
                {"drugs": i.get("drugs", []), "severity": i.get("severity", "")}
                for i in (interaction_results.get("details") or [])[:3]   # cap at 3
            ],
        }

        prompt_template = load_prompt("risk")
        prompt = (
            prompt_template
            .replace("{extracted_data}",     json.dumps(minimal_data,         separators=(',', ':')))
            .replace("{interaction_results}", json.dumps(minimal_interactions, separators=(',', ':')))
        )

        raw = call_llm(
            prompt,
            system=(
                "You are a clinical risk detection AI. Be conservative and evidence-based. "
                "Do NOT exaggerate severity. A patient with normal vitals and mild symptoms "
                "is LOW risk regardless of diagnosis wording. Return only valid JSON."
            ),
            temperature=0.0    # ← was 0.1
                 # ← added
        )

        result = parse_json_response(raw)

        level = result.get("risk_level", "moderate").lower()
        result["risk_level"] = level
        result["score"] = _score_for_level(level)

        logger.info(f"Risk assessment complete. Level: {level} | Score: {result['score']}")
        return result

    except Exception as e:
        logger.error(f"Risk detection failed: {e}", exc_info=True)
        return _fallback()


def _fallback() -> dict:
    return {
        "risk_level": "unknown",
        "score": 0,
        "risks": [],
        "immediate_action_required": False,
        "summary": "Risk assessment could not be completed — check logs.",
    }