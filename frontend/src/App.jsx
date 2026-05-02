import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './Home';
import SmartSummarization from './SmartSummarization';
import DrugInteractions from "./DrugInteractions";
import PatientRiskScore from "./PatientRiskScore";
import Contact from './Contact';

function App() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home toggleTheme={toggleTheme} theme={theme} />} />
        <Route path="/smart-summarization" element={<SmartSummarization />} />
        <Route path="/drug-interactions" element={<DrugInteractions />} />
        <Route path="/risk-prediction" element={<PatientRiskScore />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </Router>
  );
}

export default App;