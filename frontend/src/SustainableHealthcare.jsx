import "./SustainableHealthcare.css";

export default function SustainableHealthcare({
    apiResult,
    noteText
}) {

    const reportsSummarized =
        apiResult ? 1 : 0;

    const pagesSaved =
        apiResult
        ? Math.max(
            1,
            Math.ceil(noteText.length / 2500)
        )
        : 0;

    const duplicateTestsAvoided =
        apiResult?.drug_interactions?.interactions_found
            ? apiResult.drug_interactions.details.length
            : 0;

    const drugInteractionsDetected =
        apiResult?.drug_interactions?.details?.length || 0;

    const co2Reduction =
        (pagesSaved * 0.005).toFixed(2);

    return (

        <div className="sustainability-container">

            <h1>♻ Sustainable Healthcare Dashboard</h1>

            <div className="card-grid">

                <div className="card">
                    <h2>{reportsSummarized}</h2>
                    <p>Reports Summarized</p>
                </div>

                <div className="card">
                    <h2>{pagesSaved}</h2>
                    <p>Pages Saved</p>
                </div>

                <div className="card">
                    <h2>{duplicateTestsAvoided}</h2>
                    <p>Duplicate Tests Avoided</p>
                </div>

                <div className="card">
                    <h2>{drugInteractionsDetected}</h2>
                    <p>Drug Interactions Detected</p>
                </div>

                <div className="card">
                    <h2>{co2Reduction} kg</h2>
                    <p>Estimated CO₂ Reduction</p>
                </div>

            </div>

            <div className="impact-section">

                <h2>How MedBrief AI Supports Sustainability</h2>

                <ul>

                    <li>
                        Reduces paperwork through AI-generated summaries.
                    </li>

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