from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    clinical_note: str = Field(..., min_length=20, max_length=10000)
    goal: str = Field(default="full analysis", max_length=500)