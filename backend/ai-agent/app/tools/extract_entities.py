
import json
from app.services.llm_service import call_llm
from app.agent.memory import load_prompt
from app.utils.parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger("extract_entities")

def run(clinical_note: str) -> dict:
    logger.info("Starting entity extraction")
    logger.debug(f"Clinical note length: {len(clinical_note)} chars")

    try:
        prompt_template = load_prompt("extract")
        prompt = prompt_template.replace("{clinical_note}", clinical_note)
        logger.debug("Prompt loaded and formatted successfully")

        raw = call_llm(prompt, system="You are a clinical entity extraction AI. Return only valid JSON. No markdown, no explanation.")
        logger.debug(f"LLM raw response: {raw[:300]}...")

        result = parse_json_response(raw)
        logger.info(f"Extraction successful. Found {len(result.get('medications', []))} medications, {len(result.get('symptoms', []))} symptoms")
        return result

    except ValueError as e:
        logger.error(f"JSON parsing failed: {e}")
        return _fallback()
    except Exception as e:
        logger.error(f"Extraction failed with unexpected error: {e}", exc_info=True)
        return _fallback()

def _fallback() -> dict:
    return {
        "patient_name": None,
        "age": None,
        "gender": None,
        "symptoms": [],
        "diagnosis": None,
        "medications": [],
        "allergies": [],
        "vitals": {},
        "notes": "Extraction failed - please check logs.",
    }
