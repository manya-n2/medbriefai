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
