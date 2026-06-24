# app/services/sustainability_service.py

def get_sustainability_metrics():
    reports_summarized = 120
    pages_saved = reports_summarized * 7
    duplicate_tests_avoided = 18
    drug_interactions_detected = 24

    # Approximate: 1 page ≈ 5g CO₂
    co2_reduction = round((pages_saved * 5) / 1000, 2)

    return {
        "reports_summarized": reports_summarized,
        "pages_saved": pages_saved,
        "duplicate_tests_avoided": duplicate_tests_avoided,
        "drug_interactions_detected": drug_interactions_detected,
        "co2_reduction": f"{co2_reduction} kg"
    }