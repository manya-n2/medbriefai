# app/services/sustainability_service.py

def get_sustainability_metrics(
        clinical_note: str,
        interaction_count: int,
        interactions_found: bool
):

    reports_summarized = 1

    pages_saved = max(
        1,
        (len(clinical_note) + 2499) // 2500
    )

    duplicate_tests_avoided = (
        interaction_count if interactions_found else 0
    )

    drug_interactions_detected = interaction_count

    co2_reduction = round(
        pages_saved * 0.005,
        2
    )

    return {
        "reports_summarized": reports_summarized,
        "pages_saved": pages_saved,
        "duplicate_tests_avoided": duplicate_tests_avoided,
        "drug_interactions_detected": drug_interactions_detected,
        "co2_reduction": f"{co2_reduction} kg"
    }