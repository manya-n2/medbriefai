import "./SustainableHealthcare.css";

export default function SustainableHealthcare() {

    const metrics = {
        reports_summarized: 120,
        pages_saved: 840,
        duplicate_tests_avoided: 18,
        drug_interactions_detected: 24,
        co2_reduction: "4.2 kg"
    };

    return (
        <div className="sustainability-container">

            <h1>♻ Sustainable Healthcare Dashboard</h1>

            <div className="card-grid">

                <div className="card">
                    <h2>{metrics.reports_summarized}</h2>
                    <p>Reports Summarized</p>
                </div>

                <div className="card">
                    <h2>{metrics.pages_saved}</h2>
                    <p>Pages Saved</p>
                </div>

                <div className="card">
                    <h2>{metrics.duplicate_tests_avoided}</h2>
                    <p>Duplicate Tests Avoided</p>
                </div>

                <div className="card">
                    <h2>{metrics.drug_interactions_detected}</h2>
                    <p>Drug Interactions Detected</p>
                </div>

                <div className="card">
                    <h2>{metrics.co2_reduction}</h2>
                    <p>Estimated CO₂ Reduction</p>
                </div>

            </div>

            <div className="impact-section">
                <h2>How MedBrief AI Supports Sustainability</h2>

                <ul>
                    <li>Reduces paperwork through AI-generated summaries.</li>

                    <li>
                        Promotes efficient utilization of healthcare resources.
                    </li>

                    <li>
                        Helps avoid unnecessary diagnostic procedures.
                    </li>

                    <li>
                        Improves patient safety through drug interaction analysis.
                    </li>

                    <li>
                        Supports SDG 3 and SDG 12 through responsible AI.
                    </li>
                </ul>

            </div>

        </div>
    );
}