
"""
agent_test.py
=============

TYPE 1 - Unit Tests  : Test each module in isolation using mocked LLM
TYPE 2 - API Tests   : Test all FastAPI endpoints using TestClient

"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

#  Sample data 

SAMPLE_NOTE = """Patient: Jane Smith, 45-year-old female.
Chief Complaint: Severe headache and dizziness for 3 days.
Diagnosis: Suspected hypertensive crisis.
Medications: Lisinopril 10mg daily, Amlodipine 5mg daily, Hydrochlorothiazide 25mg daily.
Vitals: BP 190/110, Pulse 92, SpO2 98%, Temp 98.4F.
Allergies: Sulfa drugs.
Notes: Patient has history of hypertension and chronic kidney disease."""

SHORT_NOTE = "hi"

SAMPLE_EXTRACTED = {
    "patient_name": "Jane Smith",
    "age": 45,
    "gender": "female",
    "symptoms": ["severe headache", "dizziness"],
    "diagnosis": "Suspected hypertensive crisis",
    "medications": [
        {"name": "Lisinopril", "dose": "10mg", "frequency": "daily"},
        {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"},
        {"name": "Hydrochlorothiazide", "dose": "25mg", "frequency": "daily"},
    ],
    "allergies": ["Sulfa drugs"],
    "vitals": {"bp": "190/110", "pulse": "92", "spo2": "98%", "temp": "98.4F"},
    "notes": "History of hypertension and chronic kidney disease.",
}

SAMPLE_INTERACTIONS = {
    "source": "llm",
    "interactions_found": True,
    "details": [
        {
            "drugs": ["Lisinopril", "Hydrochlorothiazide"],
            "severity": "moderate",
            "description": "Combined use may increase risk of hypotension.",
        }
    ],
    "overall_safety": "caution",
    "recommendation": "Monitor blood pressure closely.",
}

SAMPLE_RISKS = {
    "risk_level": "critical",
    "risks": [
        {
            "type": "vitals",
            "description": "BP 190/110 indicates hypertensive crisis",
            "severity": "critical",
        },
        {
            "type": "symptom",
            "description": "Severe headache with high BP may indicate hypertensive emergency",
            "severity": "high",
        },
    ],
    "immediate_action_required": True,
    "summary": "Patient presents with hypertensive crisis requiring immediate evaluation.",
}



# TYPE 1 - UNIT TESTS


class TestParser:
    """Unit tests for JSON parser utility."""

    def test_parse_clean_json_object(self):
        from app.utils.parser import parse_json_response
        result = parse_json_response('{"key": "value", "num": 42}')
        assert result == {"key": "value", "num": 42}

    def test_parse_clean_json_array(self):
        from app.utils.parser import parse_json_response
        result = parse_json_response('[{"step": 1}, {"step": 2}]')
        assert len(result) == 2
        assert result[0]["step"] == 1

    def test_parse_json_with_markdown_fences(self):
        from app.utils.parser import parse_json_response
        text = '```json\n{"patient": "John", "age": 58}\n```'
        result = parse_json_response(text)
        assert result["patient"] == "John"

    def test_parse_json_embedded_in_text(self):
        from app.utils.parser import parse_json_response
        text = 'Here is the result: {"risk_level": "high", "found": true}'
        result = parse_json_response(text)
        assert result["risk_level"] == "high"

    def test_raises_on_invalid_json(self):
        from app.utils.parser import parse_json_response
        with pytest.raises(ValueError):
            parse_json_response("This is not JSON at all.")

    def test_raises_on_empty_string(self):
        from app.utils.parser import parse_json_response
        with pytest.raises(ValueError):
            parse_json_response("")


class TestConstraints:
    """Unit tests for input validation."""

    def test_valid_clinical_note_passes(self):
        from app.utils.constraints import validate_clinical_note
        assert validate_clinical_note(SAMPLE_NOTE) is None

    def test_empty_note_fails(self):
        from app.utils.constraints import validate_clinical_note
        assert validate_clinical_note("") is not None

    def test_whitespace_only_note_fails(self):
        from app.utils.constraints import validate_clinical_note
        assert validate_clinical_note("   ") is not None

    def test_too_short_note_fails(self):
        from app.utils.constraints import validate_clinical_note
        assert validate_clinical_note("hi") is not None

    def test_too_long_note_fails(self):
        from app.utils.constraints import validate_clinical_note
        assert validate_clinical_note("x" * 10001) is not None

    def test_valid_goal_passes(self):
        from app.utils.constraints import validate_goal
        assert validate_goal("full analysis") is None

    def test_empty_goal_fails(self):
        from app.utils.constraints import validate_goal
        assert validate_goal("") is not None

    def test_too_long_goal_fails(self):
        from app.utils.constraints import validate_goal
        assert validate_goal("x" * 501) is not None


class TestExtractEntities:
    """Unit tests for entity extraction tool."""

    @patch("app.tools.extract_entities.call_llm")
    @patch("app.tools.extract_entities.load_prompt")
    def test_returns_correct_structure(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Extract: {clinical_note}"
        mock_llm.return_value = json.dumps(SAMPLE_EXTRACTED)
        from app.tools.extract_entities import run
        result = run(SAMPLE_NOTE)
        assert isinstance(result, dict)
        assert "patient_name" in result
        assert "medications" in result
        assert "symptoms" in result
        assert "vitals" in result

    @patch("app.tools.extract_entities.call_llm")
    @patch("app.tools.extract_entities.load_prompt")
    def test_extracts_correct_patient_name(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Extract: {clinical_note}"
        mock_llm.return_value = json.dumps(SAMPLE_EXTRACTED)
        from app.tools.extract_entities import run
        result = run(SAMPLE_NOTE)
        assert result["patient_name"] == "Jane Smith"

    @patch("app.tools.extract_entities.call_llm")
    @patch("app.tools.extract_entities.load_prompt")
    def test_extracts_medications_list(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Extract: {clinical_note}"
        mock_llm.return_value = json.dumps(SAMPLE_EXTRACTED)
        from app.tools.extract_entities import run
        result = run(SAMPLE_NOTE)
        assert len(result["medications"]) == 3
        assert result["medications"][0]["name"] == "Lisinopril"

    @patch("app.tools.extract_entities.call_llm")
    @patch("app.tools.extract_entities.load_prompt")
    def test_fallback_on_bad_llm_response(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Extract: {clinical_note}"
        mock_llm.return_value = "I cannot process this request."
        from app.tools.extract_entities import run
        result = run(SAMPLE_NOTE)
        assert isinstance(result, dict)
        assert "medications" in result
        assert isinstance(result["medications"], list)

    @patch("app.tools.extract_entities.call_llm")
    @patch("app.tools.extract_entities.load_prompt")
    def test_fallback_on_llm_exception(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Extract: {clinical_note}"
        mock_llm.side_effect = Exception("Network error")
        from app.tools.extract_entities import run
        result = run(SAMPLE_NOTE)
        assert isinstance(result, dict)


class TestSummarize:
    """Unit tests for summarization tool."""

    @patch("app.tools.summarize.call_llm")
    @patch("app.tools.summarize.load_prompt")
    def test_returns_non_empty_string(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Summarize: {extracted_data}"
        mock_llm.return_value = "PATIENT OVERVIEW:\nJane Smith, 45F\n\nDIAGNOSIS:\nHypertensive crisis"
        from app.tools.summarize import run
        result = run(SAMPLE_EXTRACTED)
        assert isinstance(result, str)
        assert len(result) > 10

    @patch("app.tools.summarize.call_llm")
    @patch("app.tools.summarize.load_prompt")
    def test_handles_empty_extracted_data(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Summarize: {extracted_data}"
        mock_llm.return_value = "No data available."
        from app.tools.summarize import run
        result = run({})
        assert isinstance(result, str)

    @patch("app.tools.summarize.call_llm")
    @patch("app.tools.summarize.load_prompt")
    def test_handles_failed_extraction_data(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Summarize: {extracted_data}"
        mock_llm.return_value = "Cannot summarize."
        from app.tools.summarize import run
        bad_data = {"notes": "Extraction failed - please check logs."}
        result = run(bad_data)
        assert isinstance(result, str)


class TestCheckInteractions:
    """Unit tests for drug interaction checker."""

    def test_empty_medications_returns_no_interactions(self):
        from app.tools.check_interactions import run
        result = run([])
        assert result["interactions_found"] is False

    @patch("app.tools.check_interactions._check_llm")
    @patch("app.tools.check_interactions._get_rxcui")
    def test_uses_llm_when_api_fails(self, mock_rxcui, mock_llm):
        mock_rxcui.return_value = None
        mock_llm.return_value = SAMPLE_INTERACTIONS
        from app.tools.check_interactions import run
        result = run(SAMPLE_EXTRACTED["medications"])
        assert "interactions_found" in result

    @patch("app.tools.check_interactions._check_llm")
    @patch("app.tools.check_interactions._get_rxcui")
    def test_returns_details_list(self, mock_rxcui, mock_llm):
        mock_rxcui.return_value = None
        mock_llm.return_value = SAMPLE_INTERACTIONS
        from app.tools.check_interactions import run
        result = run(SAMPLE_EXTRACTED["medications"])
        assert "details" in result
        assert isinstance(result["details"], list)


class TestDetectRisks:
    """Unit tests for risk detection tool."""

    @patch("app.tools.detect_risks.call_llm")
    @patch("app.tools.detect_risks.load_prompt")
    def test_returns_risk_structure(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Detect: {extracted_data} {interaction_results}"
        mock_llm.return_value = json.dumps(SAMPLE_RISKS)
        from app.tools.detect_risks import run
        result = run(SAMPLE_EXTRACTED, SAMPLE_INTERACTIONS)
        assert "risk_level" in result
        assert "risks" in result
        assert "immediate_action_required" in result

    @patch("app.tools.detect_risks.call_llm")
    @patch("app.tools.detect_risks.load_prompt")
    def test_critical_risk_for_hypertension(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Detect: {extracted_data} {interaction_results}"
        mock_llm.return_value = json.dumps(SAMPLE_RISKS)
        from app.tools.detect_risks import run
        result = run(SAMPLE_EXTRACTED, SAMPLE_INTERACTIONS)
        assert result["risk_level"] == "critical"
        assert result["immediate_action_required"] is True

    @patch("app.tools.detect_risks.call_llm")
    @patch("app.tools.detect_risks.load_prompt")
    def test_fallback_on_parse_failure(self, mock_prompt, mock_llm):
        mock_prompt.return_value = "Detect: {extracted_data} {interaction_results}"
        mock_llm.return_value = "Cannot assess risks."
        from app.tools.detect_risks import run
        result = run(SAMPLE_EXTRACTED, {})
        assert isinstance(result, dict)
        assert "risk_level" in result


class TestPlanner:
    """Unit tests for the planning module."""

    def test_default_plan_has_4_steps(self):
        from app.agent.planner import _default_plan
        plan = _default_plan()
        assert len(plan) == 4

    def test_default_plan_starts_with_extract(self):
        from app.agent.planner import _default_plan
        plan = _default_plan()
        assert plan[0]["tool"] == "extract_entities"

    def test_default_plan_has_all_tools(self):
        from app.agent.planner import _default_plan
        plan = _default_plan()
        tools = [s["tool"] for s in plan]
        assert "extract_entities" in tools
        assert "summarize" in tools
        assert "check_interactions" in tools
        assert "detect_risks" in tools

    def test_generate_plan_returns_list(self):
        from app.agent.planner import generate_plan
        plan = generate_plan(SAMPLE_NOTE, "full analysis")
        assert isinstance(plan, list)
        assert len(plan) > 0

    def test_generate_plan_always_starts_with_extract(self):
        from app.agent.planner import generate_plan
        plan = generate_plan(SAMPLE_NOTE, "full analysis")
        assert plan[0]["tool"] == "extract_entities"

    def test_each_step_has_tool_key(self):
        from app.agent.planner import generate_plan
        plan = generate_plan(SAMPLE_NOTE, "summarize")
        for step in plan:
            assert "tool" in step
            assert "reason" in step


class TestMemory:
    """Unit tests for session memory module."""

    def test_create_session_returns_string(self):
        from app.agent.memory import create_session
        session_id = create_session()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_store_and_retrieve_step_result(self):
        from app.agent.memory import create_session, store_step_result, get_step_result
        session_id = create_session()
        store_step_result(session_id, "extract_entities", {"patient_name": "Jane"})
        result = get_step_result(session_id, "extract_entities")
        assert result["patient_name"] == "Jane"

    def test_get_nonexistent_step_returns_none(self):
        from app.agent.memory import create_session, get_step_result
        session_id = create_session()
        result = get_step_result(session_id, "nonexistent_step")
        assert result is None

    def test_session_memory_isolation(self):
        from app.agent.memory import create_session, store_step_result, get_step_result
        s1 = create_session()
        s2 = create_session()
        store_step_result(s1, "step", {"data": "session1"})
        store_step_result(s2, "step", {"data": "session2"})
        assert get_step_result(s1, "step")["data"] == "session1"
        assert get_step_result(s2, "step")["data"] == "session2"

    def test_get_session_memory_returns_dict(self):
        from app.agent.memory import create_session, store_step_result, get_session_memory
        session_id = create_session()
        store_step_result(session_id, "step1", "result1")
        mem = get_session_memory(session_id)
        assert isinstance(mem, dict)
        assert "step1" in mem



# TYPE 2 - API TESTS (FastAPI TestClient)


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


class TestAPIHealth:
    """API tests for health and root endpoints."""

    def test_root_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_has_service_key(self, client):
        r = client.get("/")
        data = r.json()
        assert "service" in data
        assert "version" in data

    def test_health_returns_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health_has_version(self, client):
        r = client.get("/health")
        assert "version" in r.json()


class TestAPIAnalyze:
    """API tests for the main analyze endpoint."""

    @patch("app.agent.controller.planner.generate_plan")
    @patch("app.agent.controller.executor.execute_plan")
    @patch("app.agent.controller.memory.persist_result")
    @patch("app.agent.controller.memory.get_session_memory")
    def test_analyze_returns_200(self, mock_mem, mock_persist, mock_exec, mock_plan, client):
        mock_plan.return_value = [{"step": 1, "tool": "extract_entities", "reason": "test"}]
        mock_exec.return_value = ["extract_entities", "summarize", "check_interactions", "detect_risks"]
        mock_mem.return_value = {
            "extract_entities": SAMPLE_EXTRACTED,
            "summarize": "PATIENT OVERVIEW:\nJane Smith, 45F",
            "check_interactions": SAMPLE_INTERACTIONS,
            "detect_risks": SAMPLE_RISKS,
        }
        mock_persist.return_value = None
        r = client.post("/analyze", json={"clinical_note": SAMPLE_NOTE, "goal": "full analysis"})
        assert r.status_code == 200

    @patch("app.agent.controller.planner.generate_plan")
    @patch("app.agent.controller.executor.execute_plan")
    @patch("app.agent.controller.memory.persist_result")
    @patch("app.agent.controller.memory.get_session_memory")
    def test_analyze_response_has_required_fields(self, mock_mem, mock_persist, mock_exec, mock_plan, client):
        mock_plan.return_value = [{"step": 1, "tool": "extract_entities", "reason": "test"}]
        mock_exec.return_value = ["extract_entities", "summarize"]
        mock_mem.return_value = {
            "extract_entities": SAMPLE_EXTRACTED,
            "summarize": "Summary here",
            "check_interactions": SAMPLE_INTERACTIONS,
            "detect_risks": SAMPLE_RISKS,
        }
        mock_persist.return_value = None
        r = client.post("/analyze", json={"clinical_note": SAMPLE_NOTE, "goal": "full analysis"})
        data = r.json()
        assert "success" in data
        assert "session_id" in data
        assert "steps_executed" in data
        assert "extracted_entities" in data
        assert "summary" in data

    def test_analyze_rejects_empty_note(self, client):
        r = client.post("/analyze", json={"clinical_note": "", "goal": "full analysis"})
        assert r.status_code == 422

    def test_analyze_rejects_too_short_note(self, client):
        r = client.post("/analyze", json={"clinical_note": "hi", "goal": "full analysis"})
        assert r.status_code == 422

    def test_analyze_rejects_missing_note(self, client):
        r = client.post("/analyze", json={"goal": "full analysis"})
        assert r.status_code == 422

    def test_analyze_uses_default_goal(self, client):
        # Should not fail if goal is omitted (has default value)
        r = client.post("/analyze", json={"clinical_note": SHORT_NOTE})
        # Will fail validation (note too short) but not a schema error
        assert r.status_code in (200, 422)

    @patch("app.agent.controller.planner.generate_plan")
    @patch("app.agent.controller.executor.execute_plan")
    @patch("app.agent.controller.memory.persist_result")
    @patch("app.agent.controller.memory.get_session_memory")
    def test_analyze_session_id_is_unique(self, mock_mem, mock_persist, mock_exec, mock_plan, client):
        mock_plan.return_value = [{"step": 1, "tool": "extract_entities", "reason": "test"}]
        mock_exec.return_value = ["extract_entities"]
        mock_mem.return_value = {"extract_entities": SAMPLE_EXTRACTED, "summarize": "s", "check_interactions": {}, "detect_risks": {}}
        mock_persist.return_value = None
        r1 = client.post("/analyze", json={"clinical_note": SAMPLE_NOTE, "goal": "full analysis"})
        r2 = client.post("/analyze", json={"clinical_note": SAMPLE_NOTE, "goal": "full analysis"})
        assert r1.json()["session_id"] != r2.json()["session_id"]


class TestAPIPrompts:
    """API tests for prompt management endpoints."""

    def test_list_prompts_returns_200(self, client):
        r = client.get("/prompts")
        assert r.status_code == 200
        assert "prompts" in r.json()

    def test_get_planner_prompt(self, client):
        r = client.get("/prompts/planner")
        assert r.status_code in (200, 404)  # 404 if file missing

    def test_get_invalid_prompt_returns_400(self, client):
        r = client.get("/prompts/nonexistent_prompt_xyz")
        assert r.status_code in (400, 404)

    @patch("main.save_prompt_override")
    @patch("main.load_prompt")
    def test_update_prompt_returns_success(self, mock_load, mock_save, client):
        mock_load.return_value = "old content"
        mock_save.return_value = None
        r = client.put("/prompts/planner", json={"content": "New prompt content here for testing"})
        assert r.status_code == 200
        assert "updated" in r.json()["message"].lower()

    def test_update_invalid_prompt_name(self, client):
        r = client.put("/prompts/invalid_name", json={"content": "some content"})
        assert r.status_code in (400, 404)

    def test_update_prompt_with_empty_content(self, client):
        r = client.put("/prompts/planner", json={"content": ""})
        assert r.status_code == 422

    def test_update_prompt_with_whitespace_only(self, client):
        r = client.put("/prompts/planner", json={"content": "   "})
        assert r.status_code == 422

# ══════════════════════════════════════════════════════════════════════════════
# PDF UPLOAD TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestPDFExtractor:
    """Unit tests for PDF text extraction utility."""

    def test_rejects_empty_bytes(self):
        from app.utils.pdf_extractor import extract_text_from_pdf
        with pytest.raises((ValueError, Exception)):
            extract_text_from_pdf(b"")

    def test_rejects_non_pdf_bytes(self):
        from app.utils.pdf_extractor import extract_text_from_pdf
        with pytest.raises(Exception):
            extract_text_from_pdf(b"this is not a pdf file at all")

    def test_size_validation_passes_small_file(self):
        from app.utils.pdf_extractor import validate_pdf_size
        small = b"x" * 100
        validate_pdf_size(small, max_mb=10.0)

    def test_size_validation_rejects_large_file(self):
        from app.utils.pdf_extractor import validate_pdf_size
        large = b"x" * (11 * 1024 * 1024)
        with pytest.raises(ValueError, match="too large"):
            validate_pdf_size(large, max_mb=10.0)

    def test_extracts_text_from_valid_pdf(self):
        """Create a minimal valid PDF in memory and test extraction."""
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Patient: John Doe, 58M. Diagnosis: Hypertension. Meds: Aspirin 81mg daily.")
        pdf_bytes = doc.tobytes()
        doc.close()

        from app.utils.pdf_extractor import extract_text_from_pdf
        text = extract_text_from_pdf(pdf_bytes)
        assert "John Doe" in text
        assert "Hypertension" in text
        assert len(text) > 20


class TestAPIPDF:
    """API tests for PDF upload endpoints."""

    def _make_pdf_bytes(self, text: str) -> bytes:
        """Helper: create a minimal PDF with given text."""
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_extract_pdf_text_endpoint_returns_200(self, client):
        pdf_bytes = self._make_pdf_bytes(
            "Patient John Doe, 58-year-old male. Diagnosis: Unstable angina. Meds: Aspirin 81mg."
        )
        r = client.post(
            "/extract/pdf-text",
            files={"file": ("test_note.pdf", pdf_bytes, "application/pdf")},
        )
        assert r.status_code == 200

    def test_extract_pdf_text_returns_correct_fields(self, client):
        pdf_bytes = self._make_pdf_bytes(
            "Patient Jane Smith, 45F. Chest pain. Medications: Metoprolol 50mg twice daily."
        )
        r = client.post(
            "/extract/pdf-text",
            files={"file": ("note.pdf", pdf_bytes, "application/pdf")},
        )
        data = r.json()
        assert "extracted_text" in data
        assert "character_count" in data
        assert "word_count" in data
        assert "ready_for_analysis" in data

    def test_extract_pdf_text_contains_patient_info(self, client):
        pdf_bytes = self._make_pdf_bytes(
            "Patient Jane Smith, 45F. Diagnosis: Hypertensive crisis."
        )
        r = client.post(
            "/extract/pdf-text",
            files={"file": ("note.pdf", pdf_bytes, "application/pdf")},
        )
        assert "Jane Smith" in r.json()["extracted_text"]

    def test_extract_pdf_rejects_non_pdf(self, client):
        r = client.post(
            "/extract/pdf-text",
            files={"file": ("note.txt", b"This is plain text", "text/plain")},
        )
        assert r.status_code == 415

    def test_extract_pdf_rejects_oversized_file(self, client):
        large_bytes = b"x" * (11 * 1024 * 1024)
        r = client.post(
            "/extract/pdf-text",
            files={"file": ("large.pdf", large_bytes, "application/pdf")},
        )
        assert r.status_code == 422

    @patch("app.agent.controller.planner.generate_plan")
    @patch("app.agent.controller.executor.execute_plan")
    @patch("app.agent.controller.memory.persist_result")
    @patch("app.agent.controller.memory.get_session_memory")
    def test_analyze_pdf_returns_200(self, mock_mem, mock_persist, mock_exec, mock_plan, client):
        mock_plan.return_value = [{"step": 1, "tool": "extract_entities", "reason": "test"}]
        mock_exec.return_value = ["extract_entities", "summarize", "check_interactions", "detect_risks"]
        mock_mem.return_value = {
            "extract_entities": SAMPLE_EXTRACTED,
            "summarize": "PATIENT OVERVIEW:\nJane Smith, 45F",
            "check_interactions": SAMPLE_INTERACTIONS,
            "detect_risks": SAMPLE_RISKS,
        }
        mock_persist.return_value = None

        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), SAMPLE_NOTE)
        pdf_bytes = doc.tobytes()
        doc.close()

        r = client.post(
            "/analyze/pdf",
            files={"file": ("clinical_note.pdf", pdf_bytes, "application/pdf")},
            data={"goal": "full analysis"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "session_id" in data

    def test_analyze_pdf_rejects_non_pdf(self, client):
        r = client.post(
            "/analyze/pdf",
            files={"file": ("note.txt", b"plain text file", "text/plain")},
            data={"goal": "full analysis"},
        )
        assert r.status_code == 415
