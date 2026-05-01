MAX_NOTE_LENGTH = 10000
MIN_NOTE_LENGTH = 20
MAX_GOAL_LENGTH = 500

def validate_clinical_note(note: str) -> str | None:
    if not note or not note.strip():
        return "Clinical note cannot be empty."
    if len(note) < MIN_NOTE_LENGTH:
        return f"Clinical note is too short (minimum {MIN_NOTE_LENGTH} characters)."
    if len(note) > MAX_NOTE_LENGTH:
        return f"Clinical note is too long (maximum {MAX_NOTE_LENGTH} characters)."
    return None

def validate_goal(goal: str) -> str | None:
    if not goal or not goal.strip():
        return "Goal cannot be empty."
    if len(goal) > MAX_GOAL_LENGTH:
        return f"Goal is too long (maximum {MAX_GOAL_LENGTH} characters)."
    return None