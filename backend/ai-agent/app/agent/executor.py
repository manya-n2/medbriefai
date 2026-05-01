
from app.agent import memory
from app.tools import extract_entities, summarize, check_interactions, detect_risks
from app.utils.logger import get_logger

logger = get_logger("executor")

TOOL_MAP = {
    "extract_entities":   extract_entities.run,
    "summarize":          summarize.run,
    "check_interactions": check_interactions.run,
    "detect_risks":       detect_risks.run,
}

def execute_plan(session_id: str, plan: list[dict], clinical_note: str) -> list[str]:
    executed = []

    for step in plan:
        tool_name = step.get("tool")
        if tool_name not in TOOL_MAP:
            logger.warning(f"Unknown tool: {tool_name}, skipping")
            continue

        logger.info(f"Executing step: {tool_name}")
        tool_fn = TOOL_MAP[tool_name]

        try:
            if tool_name == "extract_entities":
                result = tool_fn(clinical_note)

            elif tool_name == "summarize":
                extracted = memory.get_step_result(session_id, "extract_entities") or {}
                if not extracted:
                    logger.warning("No extracted data found for summarize step")
                result = tool_fn(extracted)

            elif tool_name == "check_interactions":
                extracted = memory.get_step_result(session_id, "extract_entities") or {}
                medications = extracted.get("medications", [])
                logger.debug(f"Medications for interaction check: {medications}")
                result = tool_fn(medications)

            elif tool_name == "detect_risks":
                extracted = memory.get_step_result(session_id, "extract_entities") or {}
                interactions = memory.get_step_result(session_id, "check_interactions") or {}
                result = tool_fn(extracted, interactions)

            else:
                result = None

            memory.store_step_result(session_id, tool_name, result)
            logger.info(f"Step {tool_name} completed successfully")
            executed.append(tool_name)

        except Exception as e:
            logger.error(f"Step {tool_name} failed: {e}", exc_info=True)
            memory.store_step_result(session_id, tool_name, {"error": str(e)})
            executed.append(tool_name)

    return executed
