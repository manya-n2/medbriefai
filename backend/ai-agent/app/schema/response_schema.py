
from pydantic import BaseModel, Field
from typing import Optional


class MedicationItem(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None


class VitalsData(BaseModel):
    bp: Optional[str] = None
    pulse: Optional[str] = None
    temp: Optional[str] = None
    spo2: Optional[str] = None
    rr: Optional[str] = None


class ExtractedEntities(BaseModel):
    patient_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    symptoms: list[str] = []
    diagnosis: Optional[str] = None
    medications: list[dict] = []
    allergies: list[str] = []
    vitals: dict = {}
    notes: Optional[str] = None


class InteractionDetail(BaseModel):
    drugs: list[str] = []
    severity: Optional[str] = None
    description: Optional[str] = None


class DrugInteractions(BaseModel):
    interactions_found: bool = False
    details: list[dict] = []
    source: Optional[str] = None
    overall_safety: Optional[str] = None
    recommendation: Optional[str] = None


class RiskItem(BaseModel):
    type: str
    description: str
    severity: str


class RiskAssessment(BaseModel):
    risk_level: str = "unknown"
    risks: list[dict] = []
    immediate_action_required: bool = False
    summary: Optional[str] = None


class AgentResponse(BaseModel):
    success: bool
    session_id: str
    goal: str
    steps_executed: list[str] = []
    extracted_entities: Optional[dict] = None
    summary: Optional[str] = None
    drug_interactions: Optional[dict] = None
    risk_assessment: Optional[dict] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "uuid-here",
                "goal": "full analysis",
                "steps_executed": ["extract_entities", "summarize", "check_interactions", "detect_risks"],
                "extracted_entities": {
                    "patient_name": "John Doe",
                    "age": 58,
                    "gender": "male",
                    "symptoms": ["chest pain", "shortness of breath"],
                    "diagnosis": "Suspected unstable angina",
                    "medications": [{"name": "Aspirin", "dose": "81mg", "frequency": "daily"}],
                    "allergies": ["Penicillin"],
                    "vitals": {"bp": "150/95", "pulse": "88", "spo2": "96%"}
                },
                "summary": "PATIENT OVERVIEW:\nJohn Doe, 58M...",
                "drug_interactions": {"interactions_found": True, "details": []},
                "risk_assessment": {"risk_level": "high", "immediate_action_required": True, "risks": []}
            }
        }
