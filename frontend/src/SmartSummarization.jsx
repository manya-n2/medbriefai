import  { useState } from 'react';
import { Link } from 'react-router-dom';
import './SmartSummarization.css';
import { analyzeNote, analyzePdf } from './services/api';

const SmartSummarization = () => {
  const [inputText, setInputText] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);

  // Mock data (demo purpose)
  const mockAIResponse = {
    patientCondition: "Hypertension & Type 2 Diabetes Management",
    simplifiedSummary:
      "The patient has been prescribed two medications to manage blood pressure and blood sugar. Take diabetes medication with food to avoid stomach issues.",
    medications: [
      { name: "Lisinopril", dosage: "10mg", frequency: "Once daily (QD)", purpose: "Blood Pressure" },
      { name: "Metformin", dosage: "500mg", frequency: "Twice daily (BID)", purpose: "Blood Sugar" }
    ],
    criticalInstructions: [
      "Take Metformin with meals.",
      "Monitor blood pressure weekly.",
      "Report dry cough if it persists."
    ],
    confidenceScore: 98
  };

  // File Upload Handler
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file.name);

      // demo autofill
      setInputText(
        "Rx: Lisinopril 10mg PO QD for HTN. Metformin 500mg PO BID w/ meals."
      );
    }
  };

  // Generate Summary
  const handleGenerateSummary = async () => {
  if (!inputText.trim() && !uploadedFile) {
    alert("Please enter text or upload a file.");
    return;
  }
  setIsProcessing(true);
  setResults(null);

  try {
    let raw;
    if (uploadedFile instanceof File) {
      raw = await analyzePdf(uploadedFile, "Generate Summary");
    } else {
      raw = await analyzeNote(inputText, "Generate Summary");
    }

    const entities = raw.extracted_entities || {};
    const meds = (entities.medications || []).map((m) => ({
      name:      m.name      || "Unknown",
      dosage:    m.dose      || "—",
      frequency: m.frequency || "—",
      purpose:   "—",          // backend doesn't return purpose; leave as placeholder
    }));

    // risks is list[{type, description, severity}]
    const criticalInstructions = (raw.risk_assessment?.risks || []).map(
      (r) => `[${r.severity?.toUpperCase() || 'INFO'}] ${r.type}: ${r.description}`
    );

    const levelToScore = { low: 96, medium: 78, high: 55, unknown: 70 };
    const level = raw.risk_assessment?.risk_level || "unknown";

    setResults({
      patientCondition: entities.diagnosis || "See summary below",
      simplifiedSummary: raw.summary || "—",
      medications: meds,
      criticalInstructions:
        criticalInstructions.length > 0
          ? criticalInstructions
          : ["No critical instructions detected."],
      confidenceScore: levelToScore[level] ?? 70,
    });
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    setIsProcessing(false);
  }
};

 

  return (
    <div className="summarization-page">

      {/* 🔙 NAVBAR */}
      <nav className="navbar glass mini-nav">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">Clinical Note Summarizer</span>
        </div>

        {/* ✅ FIXED ROUTING */}
        <Link to="/" className="back-link">
          ← Back to Dashboard
        </Link>
      </nav>

      <main className="summarizer-container">

        {/* HEADER */}
        <header className="page-header">
          <h1 className="gradient-text">Smart Prescription Summarization</h1>
          <p>
            Convert complex prescriptions into simple, structured patient instructions.
          </p>
        </header>

        <div className="workspace-grid">

          {/* LEFT: INPUT */}
          <div className="input-panel glass">
            <h3>Input Medical Text</h3>

            <textarea
              className="medical-textarea"
              placeholder="Paste prescription or doctor notes..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            <div className="divider"><span>OR</span></div>

            <label className="file-upload-area">
              <span className="upload-icon">📄</span>
              <div className="upload-text">
                <strong>Upload File</strong>
                <p>PDF, JPG, PNG</p>
              </div>
              <input
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileUpload}
                hidden
              />
            </label>

            {uploadedFile && (
              <div className="file-status">📄 {uploadedFile}</div>
            )}

            <button
              className={`btn-generate glow-hover ${isProcessing ? 'processing' : ''}`}
              onClick={handleGenerateSummary}
              disabled={isProcessing}
            >
              {isProcessing ? "Analyzing..." : "Generate Summary"}
            </button>
          </div>

          {/* RIGHT: RESULTS */}
          <div className="results-panel glass">

            {/* EMPTY */}
            {!isProcessing && !results && (
              <div className="empty-state">
                <span className="empty-icon">🧠</span>
                <p>Waiting for input...</p>
              </div>
            )}

            {/* LOADING */}
            {isProcessing && (
              <div className="processing-state">
                <div className="radar-spinner"></div>
                <p>AI is analyzing...</p>
              </div>
            )}

            {/* RESULTS */}
            {results && (
              <div className="summary-results">

                <div className="result-header">
                  <h3>Analysis Complete</h3>
                  <span className="confidence-badge">
                    {results.confidenceScore}%
                  </span>
                </div>

                <div className="result-section condition-box">
                  <h4>Condition</h4>
                  <p>{results.patientCondition}</p>
                </div>

                <div className="result-section">
                  <h4>Summary</h4>
                  <p className="simplified-text">
                    {results.simplifiedSummary}
                  </p>
                </div>

                <div className="result-section">
                  <h4>Medications</h4>
                  <div className="medication-list">
                    {results.medications.map((med, i) => (
                      <div key={i} className="med-card">
                        <div className="med-header">
                          <span className="med-name">{med.name}</span>
                          <span className="med-purpose">{med.purpose}</span>
                        </div>
                        <div className="med-details">
                          <span className="med-pill">💊 {med.dosage}</span>
                          <span className="med-pill">⏱️ {med.frequency}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="result-section warning-box">
                  <h4>⚠️ Instructions</h4>
                  <ul>
                    {results.criticalInstructions.map((inst, i) => (
                      <li key={i}>{inst}</li>
                    ))}
                  </ul>
                </div>

              </div>
            )}

          </div>

        </div>
      </main>
    </div>
  );
};

export default SmartSummarization;