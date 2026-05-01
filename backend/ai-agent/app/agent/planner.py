
from app.utils.logger import get_logger

logger = get_logger("planner")

VALID_TOOLS = {"extract_entities", "summarize", "check_interactions", "detect_risks"}


def generate_plan(clinical_note: str, goal: str) -> list[dict]:
    """
    Returns the default 4-step plan directly.
    LLM planning is skipped because the fixed pipeline covers all cases.
    The plan is deterministic and always correct for clinical note analysis.
    """
    logger.info(f"Generating plan for goal: {goal}")
    plan = _default_plan()
    logger.info(f"Plan ready: {[s['tool'] for s in plan]}")
    return plan


def _default_plan() -> list[dict]:
    return [
        {"step": 1, "tool": "extract_entities",   "reason": "Extract all medical entities from the clinical note"},
        {"step": 2, "tool": "summarize",           "reason": "Generate structured clinical summary from extracted data"},
        {"step": 3, "tool": "check_interactions",  "reason": "Check medication combinations for drug interactions"},
        {"step": 4, "tool": "detect_risks",        "reason": "Identify clinical risks and flag urgent concerns"},
    ]
