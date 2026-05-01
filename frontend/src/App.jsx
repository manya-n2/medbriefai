import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your page components
import Home from './Home';
import SmartSummarization from './SmartSummarization';
import DrugInteractions from "./DrugInteractions";

function App() {
  return (
    <Router>
      <Routes>
        {/* The main dashboard/home page */}
        <Route path="/" element={<Home />} />
        
        {/* The new smart summarization page */}
        <Route path="/smart-summarization" element={<SmartSummarization />} />
        <Route path="/drug-interactions" element={<DrugInteractions />} />
      </Routes>
    </Router>
  );
}

export default App;