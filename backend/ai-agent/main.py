from fastapi import FastAPI, HTTPException,UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.schema.request_schema import AnalyzeRequest
from app.schema.response_schema import AgentResponse
from app.agent.controller import run_agent
from app.agent.memory import load_prompt, save_prompt_override
from app.utils.constraints import validate_clinical_note, validate_goal
from app.utils.logger import get_logger
from app.utils.pdf_extractor import extract_text_from_pdf, validate_pdf_size
from app.tools import check_interactions as interaction_tool
from app.tools import detect_risks as risk_tool
from app.tools import extract_entities as extract_tool
from app.tools import summarize as summary_tool



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
Available prompt names: `planner`, `extract`, `summary`, `risk`, `interactions`, `interactions_assessment`
    """,
    version="1.0.0",
    contact={"name": "Team Synaptiq"},
    
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


# All valid prompt names across the system
VALID_PROMPTS = {
    "planner",
    "extract",
    "summary",
    "risk",
    "interactions",
    "interactions_assessment",
}


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
- `interactions` — controls drug interaction detection (LLM fallback)
- `interactions_assessment` — controls overall safety recommendation generation

MongoDB overrides take priority over `.txt` files.
    """,
)
def get_prompt(name: str):
    if name not in VALID_PROMPTS:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt '{name}' not found. Valid names: {sorted(VALID_PROMPTS)}"
        )
    try:
        content = load_prompt(name)
        return {"name": name, "content": content, "source": "db_or_file"}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt file for '{name}' not found on disk and no DB override exists."
        )


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

**Available prompt names:** `planner`, `extract`, `summary`, `risk`, `interactions`, `interactions_assessment`
    """,
)
def update_prompt(name: str, body: PromptUpdateRequest):
    if name not in VALID_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt name '{name}'. Valid: {sorted(VALID_PROMPTS)}"
        )
    if not body.content.strip():
        raise HTTPException(status_code=422, detail="Prompt content cannot be empty.")
    save_prompt_override(name, body.content)
    logger.info(f"Prompt '{name}' updated via API")
    return {"message": f"Prompt '{name}' updated successfully.", "name": name}


@app.get("/prompts", tags=["Prompts"], summary="List all available prompts")
def list_prompts():
    prompts = {}
    for name in sorted(VALID_PROMPTS):
        try:
            content = load_prompt(name)
            prompts[name] = {"available": True, "preview": content[:100] + "..."}
        except FileNotFoundError:
            prompts[name] = {"available": False}
    return {"prompts": prompts}


@app.post(
    "/analyze/pdf",
    response_model=AgentResponse,
    tags=["Agent"],
    summary="Upload a PDF and analyze it",
    description="""
Upload a clinical note or prescription as a PDF file.

The system will:
1. Extract text from the PDF automatically
2. Run the full agent pipeline (same as /analyze)
3. Return structured analysis results

**Accepted formats:** PDF files up to 10MB  
**Limitations:** Scanned/image-only PDFs without embedded text are not supported.
    """,
)
async def analyze_pdf(
    file: UploadFile = File(..., description="PDF file containing the clinical note"),
    goal: str = Form(default="full analysis", description="Analysis goal"),
):
    logger.info(f"PDF upload received: {file.filename} | content_type={file.content_type} | goal={goal}")

    # Validate file type
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(
                status_code=415,
                detail="Only PDF files are accepted. Please upload a .pdf file.",
            )

    # Read file bytes
    file_bytes = await file.read()

    # Validate size
    try:
        validate_pdf_size(file_bytes, max_mb=10.0)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))

    # Extract text from PDF
    try:
        clinical_note = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    logger.info(f"PDF text extracted: {len(clinical_note)} chars from {file.filename}")

    # Validate extracted text length
    note_error = validate_clinical_note(clinical_note)
    if note_error:
        raise HTTPException(
            status_code=422,
            detail=f"Extracted text is too short or empty. {note_error} Please check the PDF contains readable text.",
        )

    goal_error = validate_goal(goal)
    if goal_error:
        raise HTTPException(status_code=422, detail=goal_error)

    # Run the same agent pipeline
    result = run_agent(clinical_note, goal)
    logger.info(f"PDF analysis complete | session={result.session_id} | success={result.success}")
    return result


@app.post(
    "/extract/pdf-text",
    tags=["Agent"],
    summary="Extract raw text from a PDF (preview only)",
    description="""
Extract and return the raw text from a PDF without running the full analysis.

Useful for:
- Previewing what text the system can see before analyzing
- Debugging PDFs that may not extract correctly
- Frontend preview before submitting for full analysis
    """,
)
async def extract_pdf_text(
    file: UploadFile = File(..., description="PDF file to extract text from"),
):
    logger.info(f"PDF text extraction preview: {file.filename}")

    if file.content_type not in ("application/pdf", "application/octet-stream"):
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=415, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    try:
        validate_pdf_size(file_bytes, max_mb=10.0)
        text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "filename": file.filename,
        "extracted_text": text,
        "character_count": len(text),
        "word_count": len(text.split()),
        "ready_for_analysis": len(text) >= 20,
    }


class SummarizeTextRequest(BaseModel):
    clinical_note: str
    goal: str = "summarize"


@app.post(
    "/summarize/text",
    tags=["Summarization"],
    summary="Summarize a clinical note from text",
)
def summarize_text(request: SummarizeTextRequest):
    logger.info(f"Summarize text request | len={len(request.clinical_note)}")
    note_error = validate_clinical_note(request.clinical_note)
    if note_error:
        raise HTTPException(status_code=422, detail=note_error)

    extracted = extract_tool.run(request.clinical_note)
    summary = summary_tool.run(extracted)

    return {
        "success": True,
        "summary": summary,
        "extracted_entities": extracted,
        "source": "text",
    }


@app.post(
    "/summarize/pdf",
    tags=["Summarization"],
    summary="Upload a PDF and get a clinical summary",
)
async def summarize_pdf(
    file: UploadFile = File(...),
    goal: str = Form(default="summarize"),
):
    logger.info(f"Summarize PDF: {file.filename}")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files accepted.")

    file_bytes = await file.read()
    try:
        validate_pdf_size(file_bytes)
        clinical_note = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    note_error = validate_clinical_note(clinical_note)
    if note_error:
        raise HTTPException(status_code=422, detail=f"PDF text too short. {note_error}")

    extracted = extract_tool.run(clinical_note)
    summary = summary_tool.run(extracted)

    return {
        "success": True,
        "summary": summary,
        "extracted_entities": extracted,
        "source": "pdf",
        "filename": file.filename,
        "extracted_text_preview": clinical_note[:300] + "..." if len(clinical_note) > 300 else clinical_note,
    }


# ── 2. DRUG INTERACTION DETECTION PAGE ──────────────────────────

class MedicationListRequest(BaseModel):
    medications: list[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "medications": [
                    {"name": "Aspirin", "dose": "75mg", "frequency": "once daily"},
                    {"name": "Clopidogrel", "dose": "75mg", "frequency": "once daily"},
                    {"name": "Ibuprofen", "dose": "400mg", "frequency": "twice daily"},
                ]
            }
        }


@app.post(
    "/interactions/check",
    tags=["Drug Interactions"],
    summary="Check drug interactions for a list of medications",
    description="""
Check drug-drug interactions for a manually entered list of medications.

**Data sources:**
- RxNorm API (primary — real drug database)
- Clinical safety rules (for known critical pairs like Ibuprofen + Aspirin)
- LLM via `interactions.txt` prompt (editable at runtime via GET/PUT /prompts/interactions)

**Returns:** interactions list, severity levels, clinical context, safety recommendation.
    """,
)
def check_drug_interactions(request: MedicationListRequest):
    logger.info(f"Interaction check for {len(request.medications)} medications")

    if len(request.medications) < 2:
        raise HTTPException(
            status_code=422,
            detail="Please provide at least 2 medications to check for interactions.",
        )
    if len(request.medications) > 20:
        raise HTTPException(status_code=422, detail="Maximum 20 medications allowed.")

    result = interaction_tool.run(request.medications)
    return {
        "success": True,
        "medication_count": len(request.medications),
        **result,
    }


# ── 3. PATIENT RISK TRIAGE SCORE PAGE ──────────────────────────

class RiskScoreRequest(BaseModel):
    clinical_note: str

    class Config:
        json_schema_extra = {
            "example": {
                "clinical_note": "Patient Amit Verma, 60M. Severe chest pain for 3 hours. BP 170/105. History of MI. Diagnosis: ACS."
            }
        }


@app.post(
    "/risk/score",
    tags=["Risk Assessment"],
    summary="Calculate patient risk triage score (0-100)",
    description="""
Analyze a clinical note and return a numeric risk score from 0 to 100.

**Score ranges:**
- 0-25: Low risk — routine monitoring
- 26-50: Moderate risk — close observation  
- 51-75: High risk — urgent evaluation needed
- 76-100: Critical risk — immediate intervention required

Uses patient symptoms, vitals, history, and medications to calculate score.
    """,
)
def calculate_risk_score(request: RiskScoreRequest):
    logger.info(f"Risk score request | len={len(request.clinical_note)}")

    note_error = validate_clinical_note(request.clinical_note)
    if note_error:
        raise HTTPException(status_code=422, detail=note_error)

    extracted = extract_tool.run(request.clinical_note)

    medications = extracted.get("medications", [])
    interactions = interaction_tool.run(medications) if len(medications) >= 2 else {
        "interactions_found": False, "details": []
    }

    risk = risk_tool.run(extracted, interactions)
    score = _risk_level_to_score(risk, extracted, interactions)

    return {
        "success": True,
        "risk_score": score,
        "risk_level": risk.get("risk_level", "unknown"),
        "immediate_action_required": risk.get("immediate_action_required", False),
        "summary": risk.get("summary", ""),
        "risks": risk.get("risks", []),
        "score_breakdown": _build_score_breakdown(extracted, interactions, risk),
        "extracted_entities": extracted,
    }


def _risk_level_to_score(risk: dict, extracted: dict, interactions: dict) -> int:
    base_scores = {"low": 15, "moderate": 40, "high": 70, "critical": 90, "unknown": 30}
    score = base_scores.get(risk.get("risk_level", "unknown"), 30)

    vitals = extracted.get("vitals", {})
    symptoms = [s.lower() for s in extracted.get("symptoms", [])]
    risks = risk.get("risks", [])

    bp = vitals.get("bp", "")
    if bp and "/" in bp:
        try:
            systolic = int(bp.split("/")[0])
            if systolic >= 180:
                score = min(100, score + 10)
            elif systolic >= 160:
                score = min(100, score + 5)
        except ValueError:
            pass

    critical_symptoms = ["chest pain", "shortness of breath", "cardiac arrest", "stroke", "seizure"]
    for s in critical_symptoms:
        if any(s in sym for sym in symptoms):
            score = min(100, score + 5)

    if risk.get("immediate_action_required"):
        score = max(score, 65)

    if interactions.get("overall_safety") == "unsafe":
        score = min(100, score + 8)
    elif interactions.get("overall_safety") == "caution":
        score = min(100, score + 3)

    critical_risks = [r for r in risks if r.get("severity") in ("high", "critical")]
    score = min(100, score + len(critical_risks) * 2)

    return max(0, min(100, score))


def _build_score_breakdown(extracted: dict, interactions: dict, risk: dict) -> dict:
    factors = []

    risk_level = risk.get("risk_level", "unknown")
    factors.append({"factor": "AI risk assessment", "value": risk_level, "weight": "primary"})

    vitals = extracted.get("vitals", {})
    if vitals.get("bp"):
        factors.append({"factor": "Blood pressure", "value": vitals["bp"], "weight": "significant"})
    if vitals.get("pulse"):
        factors.append({"factor": "Heart rate", "value": vitals["pulse"], "weight": "moderate"})

    symptoms = extracted.get("symptoms", [])
    if symptoms:
        factors.append({"factor": "Symptoms", "value": f"{len(symptoms)} reported", "weight": "significant"})

    meds = extracted.get("medications", [])
    if meds:
        factors.append({"factor": "Medications", "value": f"{len(meds)} prescribed", "weight": "moderate"})

    if interactions.get("interactions_found"):
        n = len(interactions.get("details", []))
        factors.append({"factor": "Drug interactions", "value": f"{n} found", "weight": "significant"})

    return {"factors": factors}



@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check logs."})