# app/schema/sustainability_schema.py

from pydantic import BaseModel


class SustainabilityResponse(BaseModel):
    reports_summarized: int
    pages_saved: int
    duplicate_tests_avoided: int
    drug_interactions_detected: int
    co2_reduction: str