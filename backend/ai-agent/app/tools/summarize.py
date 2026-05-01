
import json
from app.services.llm_service import call_llm
from app.agent.memory import load_prompt
from app.utils.logger import get_logger

logger = get_logger("summarize")

def run(extracted_data: dict) -> str:
    logger.info("Starting summarization")

    if not extracted_data or extracted_data.get("notes") == "Extraction failed - please check logs.":
        logger.warning("Received empty or failed extraction data")
        return "Summary could not be generated - entity extraction failed."

    try:
        prompt_template = load_prompt("summary")
        prompt = prompt_template.replace("{extracted_data}", json.dumps(extracted_data, indent=2))

        summary = call_llm(
            prompt,
            system="You are a medical summarization AI. Write a clear structured clinical summary.",
            temperature=0.3,
        )
        logger.info("Summary generated successfully")
        logger.debug(f"Summary preview: {summary[:200]}")
        return summary

    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        return f"Summary generation failed: {str(e)}"
