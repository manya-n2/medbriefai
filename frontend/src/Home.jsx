import { useState } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';
import { analyzeNote, analyzePdf } from './services/api';

const Home = ({ toggleTheme, theme }) => {
  // State Management
  const [noteText, setNoteText] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [apiResult, setApiResult] = useState(null);
  const [error, setError] = useState(null);

  const loadingMessages = [
    "Extracting entities...",
    "Summarizing notes...",
    "Checking medications...",
    "Detecting risks...",
    "Finalizing agentic review..."
  ];

  // ── File handlers ─────────────────────────────────────────────────────────

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) setUploadedFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) setUploadedFile(file);
  };

  // ── Analyze ───────────────────────────────────────────────────────────────

  const handleAnalyzeClick = async () => {
    if (!noteText.trim() && !uploadedFile) {
      alert("Please paste clinical notes or upload a file to begin.");
      return;
    }
    setIsAnalyzing(true);
    setShowResults(false);
    setError(null);
    setApiResult(null);
    setLoadingStep(0);

    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < loadingMessages.length) {
        setLoadingStep(step);
      }
    }, 800);

    try {
      let result;
      if (uploadedFile instanceof File) {
        result = await analyzePdf(uploadedFile, "full analysis");
      } else {
        result = await analyzeNote(noteText, "full analysis");
      }
      setApiResult(result);
      setShowResults(true);
    } catch (err) {
      setError(err.message || "Analysis failed. Is the backend running?");
    } finally {
      clearInterval(interval);
      setIsAnalyzing(false);
    }
  };

  // ── Display helpers ───────────────────────────────────────────────────────

  const severityColor = (sev) => {
    switch ((sev || '').toLowerCase()) {
      case 'critical':
      case 'severe':   return '#FF4D4D';
      case 'high':     return '#FF7043';
      case 'moderate': return '#FFC107';
      default:         return '#81C784';
    }
  };

  const riskTypeIcon = (type) => {
    switch ((type || '').toLowerCase()) {
      case 'symptom':      return '🩺';
      case 'medication':   return '💊';
      case 'vitals':       return '📈';
      case 'comorbidity':  return '🏥';
      case 'missing_info': return 'ℹ️';
      default:             return '⚠️';
    }
  };

  const interactionSeverityColor = (sev) => {
    switch ((sev || '').toLowerCase()) {
      case 'severe':   return '#FF4D4D';
      case 'moderate': return '#FFC107';
      case 'mild':     return '#81C784';
      default:         return '#E2E8F0';
    }
  };

  const getDiagnosis = (result) => {
    if (!result) return '—';
    const d = result.extracted_entities?.diagnosis;
    if (d && d.trim() && d.trim().toLowerCase() !== 'null') return d.trim();
    const summary = result.summary || '';
    const match = summary.match(/DIAGNOSIS:\s*\n?([^\n]+)/i);
    if (match && match[1].trim()) return match[1].trim();
    return '—';
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="clinical-app">

      {/* 1. NAVBAR */}
      <nav className="navbar glass">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">MedBrief AI</span>
        </div>
        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
          {/* 🌙 Theme Toggle */}
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>
          <button 
            className="nav-btn-analyze glow-hover" 
            onClick={() => document.getElementById('analyze').scrollIntoView({ behavior: 'smooth' })}
          >
            Analyze
          </button>
        </div>
      </nav>

      {/* 2. HERO */}
      <section id="home" className="hero">
        <div className="glow-shape shape-1"></div>
        <div className="glow-shape shape-2"></div>
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="gradient-text">AI-Powered Clinical Note Analysis</h1>
            <p className="subheading">
              Convert complex doctor notes into structured summaries, detect medication risks, and identify dangerous drug interactions instantly utilizing autonomous agentic workflows.
            </p>
            <div className="cta-group">
              <button
                className="btn-primary glow-hover"
                onClick={() => document.getElementById('analyze').scrollIntoView({ behavior: 'smooth' })}
              >
                Analyze Notes
              </button>
            </div>
          </div>
          <div className="hero-illustration glass">
            <div className="mock-scanner">
              <div className="scanner-line"></div>
              <p>Agentic System Ready...</p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. ANALYZE PANEL */}
      <section id="analyze" className="analyze-section">
        <div className="analyze-card glass">
          <h2>Analyze Clinical Notes</h2>

          <div className="input-group">
            <textarea
              placeholder="Paste doctor notes, discharge summary, prescriptions, or medical records here..."
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
            />
          </div>

          {/* DRAG & DROP UPLOAD */}
          <div className="upload-group">
            <div
              className={`upload-area ${isDragging ? 'dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input').click()}
            >
              <span className="upload-icon">📄</span>
              <p>{isDragging ? 'Drop file here...' : 'Drag & drop or click to upload'}</p>
              <small>Accepted formats: PDF, DOCX</small>
              <input
                id="file-input"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileUpload}
                hidden
              />
            </div>
            {uploadedFile && (
              <div className="file-preview">
                ✅ File selected: {uploadedFile instanceof File ? uploadedFile.name : uploadedFile}
                <button
                  onClick={() => setUploadedFile(null)}
                  style={{ marginLeft: '0.75rem', background: 'none', border: 'none', color: '#FF4D4D', cursor: 'pointer', fontSize: '1rem' }}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            )}
          </div>

          <div className="action-group" style={{ justifyContent: 'center' }}>
            <button
              className="btn-analyze glow-hover"
              onClick={handleAnalyzeClick}
              disabled={isAnalyzing}
              style={{ flex: 'unset', width: '100%', maxWidth: '400px' }}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </section>

      {/* 4. LOADING */}
      {isAnalyzing && (
        <section className="loading-section fade-in">
          <div className="loader-container">
            <div className="spinner"></div>
            <h3>Agentic AI is analyzing clinical notes...</h3>
            <p className="loading-text">{loadingMessages[loadingStep]}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${((loadingStep + 1) / loadingMessages.length) * 100}%` }}
              />
            </div>
          </div>
        </section>
      )}

      {/* 5. RESULTS */}
      {showResults && apiResult && (
        <section className="results-section fade-in">
          <h2 className="section-title">Analysis Dashboard</h2>
          <div className="results-grid">

            {/* SUMMARY */}
            <div className="result-card glass summary-card">
              <h3>📝 Structured Summary</h3>
              <p style={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                {apiResult.summary || '—'}
              </p>
            </div>

            {/* SYMPTOMS */}
            <div className="result-card glass">
              <h3>⚠️ Extracted Symptoms</h3>
              <div className="chip-container">
                {(apiResult.extracted_entities?.symptoms || []).length > 0
                  ? apiResult.extracted_entities.symptoms.map((sym, i) => (
                      <span key={i} className="chip">{sym}</span>
                    ))
                  : <span className="chip">None detected</span>
                }
              </div>
            </div>

            {/* MEDICATIONS */}
            <div className="result-card glass">
              <h3>💊 Medications</h3>
              <div className="pill-container">
                {(apiResult.extracted_entities?.medications || []).length > 0
                  ? apiResult.extracted_entities.medications.map((med, i) => (
                      <span key={i} className="med-pill">
                        {med.name}
                        {med.dose      ? ` ${med.dose}`        : ''}
                        {med.frequency ? ` — ${med.frequency}` : ''}
                      </span>
                    ))
                  : <span className="med-pill">None detected</span>
                }
              </div>
            </div>

            {/* RISK LEVEL */}
            <div className="result-card glass risk-card">
              <h3>🚨 Patient Risk Level</h3>
              <div className={`risk-badge risk-${(apiResult.risk_assessment?.risk_level || 'low').toLowerCase()}`}>
                {(apiResult.risk_assessment?.risk_level || 'UNKNOWN').toUpperCase()}
              </div>
              {apiResult.risk_assessment?.immediate_action_required && (
                <p style={{ color: '#FF4D4D', marginTop: '0.75rem', fontWeight: 'bold', fontSize: '0.9rem' }}>
                  ⚠️ Immediate Action Required
                </p>
              )}
            </div>

            {/* DRUG INTERACTIONS */}
            <div className="result-card glass warning-card">
              <h3>🔗 Drug Interactions</h3>
              {apiResult.drug_interactions?.interactions_found
                ? <>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {(apiResult.drug_interactions.details || []).map((item, i) => (
                        <div
                          key={i}
                          style={{
                            padding: '0.6rem 0.8rem',
                            borderRadius: '8px',
                            borderLeft: `3px solid ${interactionSeverityColor(item.severity)}`,
                            background: 'rgba(0,0,0,0.15)',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                              {Array.isArray(item.drugs) ? item.drugs.join(' + ') : ''}
                            </span>
                            {item.severity && (
                              <span style={{
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                padding: '0.15rem 0.5rem',
                                borderRadius: '12px',
                                color: interactionSeverityColor(item.severity),
                                border: `1px solid ${interactionSeverityColor(item.severity)}`,
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                              }}>
                                {item.severity}
                              </span>
                            )}
                          </div>
                          {item.description && (
                            <p style={{ fontSize: '0.85rem', opacity: 0.85, margin: 0 }}>
                              {item.description}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                    {apiResult.drug_interactions.recommendation && (
                      <p style={{ marginTop: '1rem', color: '#FFC107', fontSize: '0.85rem', borderTop: '1px solid rgba(255,193,7,0.2)', paddingTop: '0.75rem' }}>
                        💡 {apiResult.drug_interactions.recommendation}
                      </p>
                    )}
                  </>
                : <p style={{ color: '#81C784' }}>✅ No clinically significant interactions detected</p>
              }
            </div>

            {/* DIAGNOSIS */}
            <div className="result-card glass">
              <h3>📋 Detected Diagnosis</h3>
              <p className="highlight-text">{getDiagnosis(apiResult)}</p>
            </div>

            {/* AI RISK INSIGHTS */}
            <div className="result-card glass full-width">
              <h3>🧠 AI Risk Insights</h3>
              {apiResult.risk_assessment?.summary && (
                <p style={{ marginBottom: '1rem', lineHeight: 1.6, opacity: 0.9 }}>
                  {apiResult.risk_assessment.summary}
                </p>
              )}
              {(apiResult.risk_assessment?.risks || []).length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {apiResult.risk_assessment.risks.map((r, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.75rem',
                        padding: '0.6rem 0.8rem',
                        borderRadius: '8px',
                        borderLeft: `3px solid ${severityColor(r.severity)}`,
                        background: 'rgba(0,0,0,0.15)',
                      }}
                    >
                      <span style={{ fontSize: '1rem', flexShrink: 0 }}>{riskTypeIcon(r.type)}</span>
                      <div>
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color: severityColor(r.severity),
                          letterSpacing: '0.5px',
                          display: 'block',
                          marginBottom: '0.15rem',
                        }}>
                          {r.type} — {r.severity}
                        </span>
                        <span style={{ fontSize: '0.88rem', opacity: 0.88 }}>
                          {r.description}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </section>
      )}

      {/* ERROR */}
      {error && (
        <section className="results-section fade-in">
          <div className="result-card glass" style={{ borderColor: 'rgba(255,77,77,0.4)', maxWidth: 600, margin: '0 auto' }}>
            <h3 style={{ color: '#FF4D4D' }}>❌ Analysis Failed</h3>
            <p style={{ margin: '0.75rem 0' }}>{error}</p>
            <small style={{ opacity: 0.6 }}>Make sure FastAPI is running at localhost:8000</small>
          </div>
        </section>
      )}

      {/* 6. FEATURES */}
      <section id="features" className="features-section">
        <h2 className="section-title">Platform Features</h2>
        <div className="feature-grid">
          {[
            { icon: "🧠", title: "Smart Summarization",      desc: "Condense long notes into key medical facts.",          link: "/smart-summarization" },
            { icon: "⚡", title: "Drug Interaction Detection", desc: "Cross-reference medications for safety.",               link: "/drug-interactions"   },
            { icon: "🚨", title: "Risk Prediction",            desc: "Identify high-risk patient indicators automatically.",  link: "/risk-prediction"     },
          ].map((feature, i) => (
            <Link key={i} to={feature.link} className="feature-card glass hover-elevate clickable-card">
              <div className="feature-icon">{feature.icon}</div>
              <h4>{feature.title}</h4>
              <p>{feature.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* 7. HOW IT WORKS */}
      <section className="workflow-section">
        <h2 className="section-title">How It Works</h2>
        <div className="timeline">
          {[
            "Upload Clinical Note",
            "AI Extracts Entities",
            "Agentic Workflow Executes",
            "Drug Safety Check",
            "Structured Summary Generated"
          ].map((step, i) => (
            <div key={i} className="timeline-step glass">
              <div className="step-number">{i + 1}</div>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 8. ABOUT */}
      <section id="about" className="about-section glass">
        <h2>About MedBrief AI</h2>
        <p>
          Built on a robust Agentic AI architecture, this platform is designed to act as an intelligent healthcare assistant.
          Our mission is to massively boost doctor productivity while maintaining a strict, safety-focused analysis pipeline.
          By automating the extraction and cross-referencing of vital patient data, we allow medical professionals to focus on what matters most: patient care.
        </p>
      </section>

      {/* 9. FOOTER */}
      <footer id="contact" className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="logo-icon">⚕️</span>
            <span>MedBrief AI</span>
          </div>
          <div className="footer-links">
            <a href="https://github.com/manya-n2/medbriefai" target="_blank" rel="noreferrer">GitHub Repo</a>
            <Link to="/Contact">Contact Us</Link>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 MedBrief AI.</p>
        </div>
      </footer>

    </div>
  );
};

export default Home;