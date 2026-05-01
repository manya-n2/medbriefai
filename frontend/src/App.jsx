import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your page components
import Home from './Home';
import SmartSummarization from './SmartSummarization';

function App() {
  return (
    <Router>
      <Routes>
        {/* The main dashboard/home page */}
        <Route path="/" element={<Home />} />
        
        {/* The new smart summarization page */}
        <Route path="/smart-summarization" element={<SmartSummarization />} />
      </Routes>
    </Router>
  );
}

export default App;