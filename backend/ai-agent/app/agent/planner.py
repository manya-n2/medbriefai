from app.utils.logger import get_logger

logger = get_logger("planner")

VALID_TOOLS = {"extract_entities", "summarize", "check_interactions", "detect_risks"}

# Maps goal keywords → which tools to skip
GOAL_TOOL_MAP = {
    "generate summary":        ["extract_entities", "summarize"],
    "detect drug interactions": ["extract_entities", "check_interactions"],
    "risk detection":          ["extract_entities", "detect_risks"],
    "extract symptoms":        ["extract_entities"],
    "full analysis":           ["extract_entities", "summarize", "check_interactions", "detect_risks"],
}

def generate_plan(clinical_note: str, goal: str) -> list[dict]:
    logger.info(f"Generating plan for goal: {goal}")

    goal_lower = goal.lower().strip()

    # Match goal to tool list
    tools = None
    for key, tool_list in GOAL_TOOL_MAP.items():
        if key in goal_lower:
            tools = tool_list
            break

    # Default to full pipeline if no match
    if tools is None:
        tools = ["extract_entities", "summarize", "check_interactions", "detect_risks"]

    plan = [
        {"step": i + 1, "tool": tool, "reason": _reason(tool)}
        for i, tool in enumerate(tools)
    ]

    logger.info(f"Plan ready: {[s['tool'] for s in plan]}")
    return plan


def _reason(tool: str) -> str:
    return {
        "extract_entities":   "Extract all medical entities from the clinical note",
        "summarize":          "Generate structured clinical summary from extracted data",
        "check_interactions": "Check medication combinations for drug interactions",
        "detect_risks":       "Identify clinical risks and flag urgent concerns",
    }.get(tool, "Execute tool")