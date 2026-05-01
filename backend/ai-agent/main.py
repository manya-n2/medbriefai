
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.schema.request_schema import AnalyzeRequest
from app.schema.response_schema import AgentResponse
from app.agent.controller import run_agent
from app.agent.memory import load_prompt, save_prompt_override
from app.utils.constraints import validate_clinical_note, validate_goal
from app.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="Clinical Note Summarizer — AI Agent",
    description="""
## Clinical Note Summarizer

An agentic AI system that analyzes clinical notes and extracts:
- **Patient entities** (name, age, medications, symptoms, vitals)
- **Structured summary** for quick doctor review  
- **Drug interactions** via RxNorm API + LLM fallback
- **Risk assessment** with severity levels

### How the Agent Works
1. **Planner** decides which tools to run
2. **Executor** runs each tool in sequence
3. **Memory** stores intermediate results per session
4. **MongoDB** persists all results and prompt overrides

### Prompt Editing
All prompts are editable at runtime via `GET/PUT /prompts/{name}`.
Available prompt names: `planner`, `extract`, `summary`, `risk`
    """,
    version="1.0.0",
    contact={"name": "Team VEERSA", "email": "team@example.com"},
    license_info={"name": "MIT"},
)

# CORS — allow all origins for hackathon (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Clinical Note Summarizer — AI Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "clinical-note-agent", "version": "1.0.0"}


@app.post(
    "/analyze",
    response_model=AgentResponse,
    tags=["Agent"],
    summary="Analyze a clinical note",
    description="""
Run the full AI agent pipeline on a clinical note.

The agent will:
1. Extract medical entities (patient info, symptoms, medications, vitals)
2. Generate a structured clinical summary
3. Check drug interactions (RxNorm API + LLM fallback)
4. Detect clinical risks and flag urgent concerns

Returns a structured JSON response with all results.
    """,
    responses={
        200: {"description": "Successful analysis"},
        422: {"description": "Validation error — note too short/long or goal too long"},
        500: {"description": "Internal agent error"},
    },
)
def analyze(request: AnalyzeRequest):
    logger.info(f"Received analyze request | goal={request.goal} | note_len={len(request.clinical_note)}")
    note_error = validate_clinical_note(request.clinical_note)
    if note_error:
        logger.warning(f"Validation failed: {note_error}")
        raise HTTPException(status_code=422, detail=note_error)
    goal_error = validate_goal(request.goal)
    if goal_error:
        logger.warning(f"Goal validation failed: {goal_error}")
        raise HTTPException(status_code=422, detail=goal_error)
    result = run_agent(request.clinical_note, request.goal)
    logger.info(f"Response sent | success={result.success} | session={result.session_id}")
    return result


@app.get(
    "/prompts/{name}",
    tags=["Prompts"],
    summary="Get a prompt by name",
    description="""
Retrieve the current content of an agent prompt.

Available prompt names:
- `planner` — controls how the agent plans steps
- `extract` — controls entity extraction from clinical notes  
- `summary` — controls how summaries are structured
- `risk` — controls risk detection and scoring

MongoDB overrides take priority over `.txt` files.
    """,
)
def get_prompt(name: str):
    try:
        content = load_prompt(name)
        return {"name": name, "content": content, "source": "db_or_file"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found. Valid names: planner, extract, summary, risk")


class PromptUpdateRequest(BaseModel):
    content: str


@app.put(
    "/prompts/{name}",
    tags=["Prompts"],
    summary="Update a prompt at runtime",
    description="""
Update an agent prompt without restarting the server.

The new content is saved to MongoDB and takes priority over the `.txt` file.
This allows reviewers to modify agent behavior on the fly.

**Available prompt names:** `planner`, `extract`, `summary`, `risk`
    """,
)
def update_prompt(name: str, body: PromptUpdateRequest):
    VALID_PROMPTS = {"planner", "extract", "summary", "risk"}
    if name not in VALID_PROMPTS:
        raise HTTPException(status_code=400, detail=f"Invalid prompt name '{name}'. Valid: {sorted(VALID_PROMPTS)}")
    if not body.content.strip():
        raise HTTPException(status_code=422, detail="Prompt content cannot be empty.")
    save_prompt_override(name, body.content)
    logger.info(f"Prompt '{name}' updated via API")
    return {"message": f"Prompt '{name}' updated successfully.", "name": name}


@app.get("/prompts", tags=["Prompts"], summary="List all available prompts")
def list_prompts():
    prompts = {}
    for name in ["planner", "extract", "summary", "risk"]:
        try:
            content = load_prompt(name)
            prompts[name] = {"available": True, "preview": content[:100] + "..."}
        except FileNotFoundError:
            prompts[name] = {"available": False}
    return {"prompts": prompts}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check logs."})
