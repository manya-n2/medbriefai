
import json
from app.services.llm_service import call_llm
from app.agent.memory import load_prompt
from app.utils.parser import parse_json_response
from app.utils.logger import get_logger

logger = get_logger("detect_risks")

def run(extracted_data: dict, interaction_results: dict) -> dict:
    logger.info("Starting risk detection")

    try:
        prompt_template = load_prompt("risk")
        prompt = (
            prompt_template
            .replace("{extracted_data}", json.dumps(extracted_data, indent=2))
            .replace("{interaction_results}", json.dumps(interaction_results, indent=2))
        )

        raw = call_llm(prompt, system="You are a clinical risk detection AI. Return only valid JSON.", temperature=0.1)
        logger.debug(f"Risk LLM raw: {raw[:300]}")

        result = parse_json_response(raw)
        logger.info(f"Risk assessment complete. Level: {result.get('risk_level')} | Immediate action: {result.get('immediate_action_required')}")
        return result

    except ValueError as e:
        logger.error(f"Risk JSON parsing failed: {e}")
        return _fallback()
    except Exception as e:
        logger.error(f"Risk detection failed: {e}", exc_info=True)
        return _fallback()

def _fallback() -> dict:
    return {
        "risk_level": "unknown",
        "risks": [],
        "immediate_action_required": False,
        "summary": "Risk assessment could not be completed - check logs.",
    }
