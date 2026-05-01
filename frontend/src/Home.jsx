import React, { useState, useEffect } from 'react';
import './Home.css';

const Home = () => {
  // State Management
  const [noteText, setNoteText] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [analysisGoal, setAnalysisGoal] = useState('Full Analysis');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [showResults, setShowResults] = useState(false);

  const loadingMessages = [
    "Extracting entities...",
    "Summarizing notes...",
    "Checking medications...",
    "Detecting risks...",
    "Finalizing agentic review..."
  ];
   // Mock Results Data
  const mockResults = {
    summary: "Patient presents with acute exacerbation of chronic obstructive pulmonary disease (COPD). Reports increased shortness of breath and productive cough over the last 3 days. Denies chest pain. Vitals indicate mild tachycardia and decreased oxygen saturation.",
    symptoms: ["Shortness of breath", "Productive cough", "Tachycardia", "Hypoxia"],
    medications: ["Albuterol 90mcg inhaler", "Prednisone 40mg", "Azithromycin 250mg"],
    riskLevel: "HIGH",
    drugInteractions: ["Albuterol + Azithromycin: Monitor for potential QT prolongation."],
    diagnosis: "Acute Exacerbation of COPD",
    insights: "Agentic analysis suggests prioritizing continuous pulse oximetry and considering a nebulized bronchodilator trial before discharge."
  };
  // Handlers
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file.name);
    }
  };

  const handleAnalyzeClick = () => {
    if (!noteText.trim() && !uploadedFile) {
      alert("Please paste clinical notes or upload a file to begin.");
      return;
    }

    setIsAnalyzing(true);
    setShowResults(false);
    setLoadingStep(0);
    // Simulate Agentic Workflow Progression
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < loadingMessages.length) {
        setLoadingStep(step);
      } else {
        clearInterval(interval);
        setIsAnalyzing(false);
        setShowResults(true);
      }
    }, 800);
  };

   return (
    <div className="clinical-app">
      {/* 1. NAVBAR */}
      <nav className="navbar glass">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">Clinical Note Summarizer</span>
        </div>
        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
          <button className="nav-btn-analyze glow-hover" onClick={() => document.getElementById('analyze').scrollIntoView({ behavior: 'smooth' })}>
            Analyze
          </button>
        </div>
      </nav>
      {/* 2. HERO SECTION */}
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
              <button className="btn-primary glow-hover" onClick={() => document.getElementById('analyze').scrollIntoView({ behavior: 'smooth' })}>
                Analyze Notes
              </button>
              <button className="btn-secondary">Learn More</button>
            </div>
          </div>
          <div className="hero-illustration glass">
            {/* Placeholder for Medical AI Illustration */}
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
            ></textarea>
          </div>

          <div className="upload-group">
            <label className="upload-area">
              <span className="upload-icon">📄</span>
              <p>Drag & drop or click to upload</p>
              <small>Accepted formats: PDF, DOCX, TXT</small>
              <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} hidden />
            </label>
            {uploadedFile && <div className="file-preview">File selected: {uploadedFile}</div>}
          </div>

          <div className="action-group">
            <select 
              className="goal-select" 
              value={analysisGoal} 
              onChange={(e) => setAnalysisGoal(e.target.value)}
            >
              <option value="Generate Summary">Generate Summary</option>
              <option value="Detect Drug Interactions">Detect Drug Interactions</option>
              <option value="Risk Detection">Risk Detection</option>
              <option value="Extract Symptoms">Extract Symptoms</option>
              <option value="Full Analysis">Full Analysis</option>
            </select>
            <button className="btn-analyze glow-hover" onClick={handleAnalyzeClick}>
              Analyze
            </button>
          </div>
        </div>
      </section>
      {/* 4. LOADING SECTION */}
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
              ></div>
            </div>
          </div>
        </section>
      )}
      {/* 5. RESULTS SECTION */}
      {showResults && (
        <section className="results-section fade-in">
          <h2 className="section-title">Analysis Dashboard</h2>
          <div className="results-grid">
            
            <div className="result-card glass summary-card">
              <h3>📝 Structured Summary</h3>
              <p>{mockResults.summary}</p>
            </div>

            <div className="result-card glass">
              <h3>⚠️ Extracted Symptoms</h3>
              <div className="chip-container">
                {mockResults.symptoms.map((sym, i) => <span key={i} className="chip">{sym}</span>)}
              </div>
            </div>

            <div className="result-card glass">
              <h3>💊 Medications</h3>
              <div className="pill-container">
                {mockResults.medications.map((med, i) => <span key={i} className="med-pill">{med}</span>)}
              </div>
            </div>

            <div className="result-card glass risk-card">
              <h3>🚨 Patient Risk Level</h3>
              <div className={`risk-badge risk-${mockResults.riskLevel.toLowerCase()}`}>
                {mockResults.riskLevel}
              </div>
            </div>

            <div className="result-card glass warning-card">
              <h3>🔗 Drug Interactions</h3>
              <ul className="warning-list">
                {mockResults.drugInteractions.map((interaction, i) => <li key={i}>{interaction}</li>)}
              </ul>
            </div>

            <div className="result-card glass">
              <h3>📋 Detected Diagnosis</h3>
              <p className="highlight-text">{mockResults.diagnosis}</p>
            </div>

            <div className="result-card glass full-width">
              <h3>🧠 AI Insights & Recommendations</h3>
              <p>{mockResults.insights}</p>
            </div>

          </div>
        </section>
      )}
      {/* 6. FEATURES SECTION */}
      <section id="features" className="features-section">
        <h2 className="section-title">Platform Features</h2>
        <div className="feature-grid">
          {[
            { icon: "🧠", title: "Smart Summarization", desc: "Condense long notes into key medical facts.", link: "/smart-summarization" },
            { icon: "⚡", title: "Drug Interaction Detection", desc: "Cross-reference medications for safety.", link: "/drug-interactions" },
            { icon: "🚨", title: "Risk Prediction", desc: "Identify high-risk patient indicators automatically.", link: "/risk-prediction" },
            { icon: "📊", title: "Structured Outputs", desc: "Export data to EHR-friendly formats.", link: "/structured-outputs" },
            { icon: "📝", title: "Prompt Editing", desc: "Refine AI outputs with custom medical prompts.", link: "/prompt-editing" },
            { icon: "⏱️", title: "Faster Clinical Review", desc: "Save hours of documentation time per shift.", link: "/clinical-review" },
            { icon: "🤖", title: "AI-Powered Agent Workflow", desc: "Multi-step autonomous reasoning for accuracy.", link: "/agent-workflow" },
            { icon: "🗣️", title: "Medical Language Simplification", desc: "Translate jargon for patient communication.", link: "/language-simplification" }
          ].map((feature, i) => (
            <a key={i} href={feature.link} className="feature-card glass hover-elevate clickable-card">
              <div className="feature-icon">{feature.icon}</div>
              <h4>{feature.title}</h4>
              <p>{feature.desc}</p>
            </a>
          ))}
        </div>
      </section>

      {/* 7. HOW IT WORKS SECTION */}
      <section className="workflow-section">
        <h2 className="section-title">How It Works</h2>
        <div className="timeline">
          {["Upload Clinical Note", "AI Extracts Entities", "Agentic Workflow Executes", "Drug Safety Check", "Structured Summary Generated"].map((step, i) => (
            <div key={i} className="timeline-step glass">
              <div className="step-number">{i + 1}</div>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 8. ABOUT SECTION */}
      <section id="about" className="about-section glass">
        <h2>About Clinical Note Summarizer</h2>
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
            <span>Clinical Note Summarizer</span>
          </div>
          <div className="footer-links">
            <a href="#home">Quick Links</a>
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub Repo</a>
            <a href="mailto:contact@example.com">Contact Us</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 Clinical Note Summarizer. Hackathon Demo.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;