import  { useState } from 'react';
import { Link } from 'react-router-dom';
import './DrugInteractions.css';
import { analyzeNote } from './services/api';

const DrugInteractions = () => {
  const [currentDrug, setCurrentDrug] = useState('');
  const [medications, setMedications] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  // Add a drug to the list
  const handleAddDrug = (e) => {
    e.preventDefault();
    if (currentDrug.trim() && !medications.includes(currentDrug.trim())) {
      setMedications([...medications, currentDrug.trim()]);
      setCurrentDrug('');
      setResults(null); // Reset results when list changes
    }
  };

  // Remove a drug from the list
  const handleRemoveDrug = (drugToRemove) => {
    setMedications(medications.filter(drug => drug !== drugToRemove));
    setResults(null);
  };

  // Simulate AI Analysis
 const handleAnalyze = async () => {
  if (medications.length < 2) {
    alert("Please add at least two medications to check for interactions.");
    return;
  }
  setIsAnalyzing(true);
  setResults(null);

  // Build a minimal note the backend can parse
  const syntheticNote =
    `Patient is currently taking the following medications: ${medications.join(", ")}.`;

  try {
    const raw = await analyzeNote(syntheticNote, "Detect Drug Interactions");
    const di = raw.drug_interactions || {};

    // overall_safety from backend: "safe" | "caution" | "unsafe"
    const safetyMap = { safe: "SAFE", caution: "WARNING", unsafe: "DANGER" };
    const status = di.interactions_found
      ? safetyMap[di.overall_safety] || "WARNING"
      : "SAFE";

    const titleMap = {
      SAFE:    "No Known Interactions",
      WARNING: "Moderate Risk: Monitor Patient",
      DANGER:  "Major Interaction Detected",
    };

    // details is list[{drugs, severity, description}]
    const description = di.interactions_found
      ? (di.details || [])
          .map((d) => {
            const pair = Array.isArray(d.drugs) ? d.drugs.join(" + ") : "";
            return `${pair}${d.severity ? ` [${d.severity}]` : ""}${d.description ? `: ${d.description}` : ""}`;
          })
          .join("\n")
      : `No significant interactions found between: ${medications.join(", ")}.`;

    // Use top-level recommendation + per-interaction descriptions as alternatives
    const alternatives = [
      di.recommendation,
      ...(di.details || []).map((d) => d.description).filter(Boolean),
    ].filter(Boolean);

    setResults({ status, title: titleMap[status], description, alternatives });
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    setIsAnalyzing(false);
  }
};

  return (
    <div className="interactions-page">
      {/* NAVBAR */}
      <nav className="navbar glass mini-nav">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">MedBrief AI</span>
        </div>
        <Link to="/" className="back-link">← Back to Dashboard</Link>
      </nav>

      <main className="interactions-container">
        <header className="page-header">
          <h1 className="gradient-text">Drug Interaction Safety Check</h1>
          <p>Cross-reference patient prescriptions instantly to prevent adverse drug events.</p>
        </header>

        <div className="workspace-grid">
          
          {/* LEFT SIDE: INPUT AREA */}
          <div className="input-panel glass">
            <h3>Add Medications</h3>
            <p className="helper-text">Type a medication name and press Enter to add it to the interaction check list.</p>
            
            <form onSubmit={handleAddDrug} className="add-drug-form">
              <input 
                type="text" 
                className="drug-input"
                placeholder="e.g., Warfarin, Aspirin, Lisinopril..."
                value={currentDrug}
                onChange={(e) => setCurrentDrug(e.target.value)}
              />
              <button type="submit" className="btn-add-drug">Add</button>
            </form>

            <div className="drug-list-container">
              <h4>Current Prescription List</h4>
              {medications.length === 0 ? (
                <p className="empty-list">No medications added yet.</p>
              ) : (
                <div className="drug-chips">
                  {medications.map((drug, idx) => (
                    <div key={idx} className="drug-chip">
                      💊 {drug}
                      <button 
                        className="btn-remove" 
                        onClick={() => handleRemoveDrug(drug)}
                        aria-label="Remove drug"
                      >×</button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button 
              className={`btn-analyze glow-hover ${isAnalyzing || medications.length < 2 ? 'disabled' : ''}`}
              onClick={handleAnalyze}
              disabled={isAnalyzing || medications.length < 2}
            >
              {isAnalyzing ? 'Cross-referencing databases...' : 'Check for Interactions'}
            </button>
          </div>

          {/* RIGHT SIDE: RESULTS AREA */}
          <div className="results-panel glass">
            {!isAnalyzing && !results && (
              <div className="empty-state">
                <span className="empty-icon">🧪</span>
                <p>Add at least 2 medications to check for interactions.</p>
                <small>Try "Warfarin" + "Aspirin" to see a major alert.</small>
              </div>
            )}

            {isAnalyzing && (
              <div className="processing-state fade-in">
                <div className="radar-spinner"></div>
                <p>Agent scanning pharmacology databases...</p>
                <p>Analyzing molecular pathways...</p>
              </div>
            )}

            {results && (
              <div className={`interaction-results fade-in status-${results.status.toLowerCase()}`}>
                <div className="result-header">
                  <span className="status-icon">
                    {results.status === 'DANGER' ? '🚨' : results.status === 'WARNING' ? '⚠️' : '✅'}
                  </span>
                  <h3>{results.title}</h3>
                </div>

                <div className="result-body">
                  <p className="interaction-desc">{results.description}</p>
                </div>

                {results.alternatives.length > 0 && (
                  <div className="alternatives-section">
                    <h4>💡 AI Agent Recommendations</h4>
                    <ul className="alternatives-list">
                      {results.alternatives.map((alt, idx) => (
                        <li key={idx}>
                          <span className="bullet-icon">👉</span>
                          {alt}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default DrugInteractions;