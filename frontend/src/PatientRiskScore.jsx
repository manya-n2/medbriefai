import  { useState } from 'react';
import { Link } from 'react-router-dom';
import './PatientRiskScore.css';
import { analyzeNote } from './services/api';

const PatientRiskScore = () => {
  const [clinicalNote, setClinicalNote] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  // Auto-fill some demo text to make presenting easier
  const loadDemoText = () => {
    setClinicalNote("Patient is a 65-year-old male presenting with severe chest pain radiating to the left arm. History of chronic hypertension and Type 2 Diabetes. Currently taking Lisinopril, Metformin, and recently started on Ibuprofen for joint pain. Patient appears diaphoretic.");
  };

  const handleCalculate = async () => {
  if (!clinicalNote.trim()) {
    alert("Please enter a clinical note to analyze.");
    return;
  }
  setIsAnalyzing(true);
  setResult(null);

  try {
    const raw = await analyzeNote(clinicalNote, "Risk Detection");

    const risk     = raw.risk_assessment || {};
    const entities = raw.extracted_entities || {};
    const level    = (risk.risk_level || "low").toUpperCase();

    const colorMap = { HIGH: "risk-high", MEDIUM: "risk-medium", LOW: "risk-low" };
    const scoreMap = { HIGH: 78, MEDIUM: 52, LOW: 22 };

    // risks is list[{type, description, severity}] — use description as reasons
    const reasons = (risk.risks || []).map(
      (r) => `${r.type}: ${r.description}`
    );

    setResult({
      score:      scoreMap[level] ?? 50,
      level,
      colorClass: colorMap[level] ?? "risk-low",
      reasons:    reasons.length > 0 ? reasons : ["No specific risk factors identified."],
      factors: {
        symptoms:     entities.symptoms?.length > 0 ? "Detected" : "None",
        medications:  entities.medications?.length || 0,
        age:          entities.age ?? "—",
        interactions: raw.drug_interactions?.interactions_found
                        ? (raw.drug_interactions.details?.length || 1)
                        : 0,
      },
    });
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    setIsAnalyzing(false);
  }
};

  return (
    <div className="risk-page">
      {/* NAVBAR */}
      <nav className="navbar glass mini-nav">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">MedBrief AI</span>
        </div>
        <Link to="/" className="back-link">← Back to Dashboard</Link>
      </nav>

      <main className="risk-container">
        <header className="page-header">
          <h1 className="gradient-text">Patient Risk Triage Score</h1>
          <p>Quantify patient risk instantly using NLP analysis of symptoms, history, and medications.</p>
        </header>

        <div className="workspace-grid">
          
          {/* LEFT SIDE: INPUT AREA */}
          <div className="input-panel glass">
            <div className="panel-header">
              <h3>Input Clinical Note</h3>
              <button className="btn-demo" onClick={loadDemoText}>Load Demo Data</button>
            </div>
            
            <textarea 
              className="medical-textarea"
              placeholder="Paste patient history, clinical notes, or triage intake form here to calculate risk score..."
              value={clinicalNote}
              onChange={(e) => setClinicalNote(e.target.value)}
            ></textarea>

            <button 
              className={`btn-analyze glow-hover ${isAnalyzing ? 'processing' : ''}`}
              onClick={handleCalculate}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Agent Calculating Risk Vectors...' : 'Calculate Risk Score'}
            </button>
          </div>

          {/* RIGHT SIDE: RESULTS AREA */}
          <div className="results-panel glass">
            {!isAnalyzing && !result && (
              <div className="empty-state">
                <span className="empty-icon">📊</span>
                <p>Awaiting clinical data...</p>
                <small>The AI will generate a score from 0-100 based on severity.</small>
              </div>
            )}

            {isAnalyzing && (
              <div className="processing-state fade-in">
                <div className="radar-spinner"></div>
                <p>Weighting symptom severity...</p>
                <p>Cross-referencing keywords...</p>
              </div>
            )}

            {result && (
              <div className="risk-results fade-in">
                
                {/* TOP HALF: THE GAUGE */}
                <div className="score-hero">
                  <div className={`score-gauge ${result.colorClass}`}>
                    <svg viewBox="0 0 36 36" className="circular-chart">
                      <path className="circle-bg"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path className="circle"
                        strokeDasharray={`${result.score}, 100`}
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <text x="18" y="20.35" className="percentage">{result.score}</text>
                    </svg>
                  </div>
                  
                  <div className="score-details">
                    <h2 className="risk-level-text">Risk Level: {result.level}</h2>
                    <p className="score-subtext">Score: {result.score}/100</p>
                  </div>
                </div>

                {/* BOTTOM HALF: THE REASONING */}
                <div className="reasoning-section">
                  <h4>🧠 AI Reasoning Matrix</h4>
                  <ul className="reasons-list">
                    {result.reasons.map((reason, idx) => (
                      <li key={idx}>
                        <span className="alert-icon">🚨</span>
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* EXTRA DATA CHIPS */}
                <div className="factors-section">
                  <h4>Key Factors Detected</h4>
                  <div className="factor-chips">
                    <span className="factor-chip">Symptoms: {result.factors.symptoms}</span>
                    <span className="factor-chip">Age: {result.factors.age}</span>
                    <span className="factor-chip">Meds: {result.factors.medications}</span>
                    <span className="factor-chip">Interactions: {result.factors.interactions}</span>
                  </div>
                </div>

              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default PatientRiskScore;