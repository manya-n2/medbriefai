"""
Memory module — manages:
1. Prompt loading (file default → MongoDB override)
2. Intermediate step result storage per session
3. Persisting final results to MongoDB
"""

import os
import uuid
from datetime import datetime
from pymongo import MongoClient
from app.config.settings import MONGO_URI, MONGO_DB, PROMPTS_DIR

# ---------------------------------------------------------------------------
# MongoDB setup (synchronous client — fine for agent internals)
# ---------------------------------------------------------------------------
_mongo_client = None
_db = None


def get_db():
    global _mongo_client, _db
    if _db is None:
        _mongo_client = MongoClient(MONGO_URI)
        _db = _mongo_client[MONGO_DB]
    return _db


# ---------------------------------------------------------------------------
# Prompt loading: file → DB override
# ---------------------------------------------------------------------------

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template by name (e.g. 'planner', 'extract').
    Checks MongoDB prompts collection first; falls back to .txt file.
    """
    db = get_db()
    doc = db.prompts.find_one({"name": prompt_name})
    if doc and doc.get("content"):
        return doc["content"]

    # Fallback: read from file
    file_path = os.path.join(PROMPTS_DIR, f"{prompt_name}.txt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_prompt_override(prompt_name: str, content: str) -> None:
    """Upsert a prompt override in MongoDB."""
    db = get_db()
    db.prompts.update_one(
        {"name": prompt_name},
        {"$set": {"name": prompt_name, "content": content, "updated_at": datetime.utcnow()}},
        upsert=True,
    )


# ---------------------------------------------------------------------------
# Session-level intermediate memory (in-process dict)
# ---------------------------------------------------------------------------

_session_store: dict[str, dict] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _session_store[session_id] = {}
    return session_id


def store_step_result(session_id: str, step: str, result) -> None:
    if session_id not in _session_store:
        _session_store[session_id] = {}
    _session_store[session_id][step] = result


def get_step_result(session_id: str, step: str):
    return _session_store.get(session_id, {}).get(step)


def get_session_memory(session_id: str) -> dict:
    return _session_store.get(session_id, {})


# ---------------------------------------------------------------------------
# Persist final result to MongoDB
# ---------------------------------------------------------------------------

def persist_result(session_id: str, clinical_note: str, goal: str, result: dict) -> None:
    db = get_db()
    db.results.insert_one({
        "session_id": session_id,
        "clinical_note": clinical_note,
        "goal": goal,
        "result": result,
        "created_at": datetime.utcnow(),
    })

def get_session_result(session_id: str) -> dict | None:
    """Retrieve a persisted session result from MongoDB."""
    db = get_db()
    doc = db.results.find_one({"session_id": session_id})
    if not doc:
        return None
    doc.pop("_id", None)
    return doc