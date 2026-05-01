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
