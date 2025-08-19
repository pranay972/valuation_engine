import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AnalysisSelection from './pages/AnalysisSelection';
import InputForm from './pages/InputForm';
import Results from './pages/Results';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<AnalysisSelection />} />
        <Route path="/analysis/:analysisType" element={<InputForm />} />
        <Route path="/results/:analysisId" element={<Results />} />
      </Routes>
    </div>
  );
}

export default App; 