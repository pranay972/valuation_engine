import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function AnalysisSelection() {
  const [analysisTypes, setAnalysisTypes] = useState([]);
  const [selectedAnalyses, setSelectedAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalysisTypes();
  }, []);

  const fetchAnalysisTypes = async () => {
    try {
      const response = await axios.get('/api/analysis/types');
      setAnalysisTypes(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load analysis types');
      setLoading(false);
    }
  };

  const handleCheckboxChange = (analysis) => {
    setSelectedAnalyses(prev => {
      const isSelected = prev.find(item => item.id === analysis.id);
      if (isSelected) {
        return prev.filter(item => item.id !== analysis.id);
      } else {
        return [...prev, analysis];
      }
    });
  };

  const handleContinue = () => {
    if (selectedAnalyses.length === 0) {
      alert('Please select at least one analysis type');
      return;
    }
    
    // Navigate with selected analyses as URL parameters
    const analysisIds = selectedAnalyses.map(a => a.id).join(',');
    navigate(`/analysis/${analysisIds}`);
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h2>Loading analysis types...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h2>Error: {error}</h2>
          <button className="button" onClick={fetchAnalysisTypes}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Financial Valuation Analysis</h1>
      <p>Select one or more analysis types to begin:</p>
      
      <div className="grid">
        {analysisTypes.map((analysis) => {
          const isSelected = selectedAnalyses.find(item => item.id === analysis.id);
          return (
            <div key={analysis.id} className={`card ${isSelected ? 'selected' : ''}`}>
              <div className="checkbox-container">
                <input
                  type="checkbox"
                  id={analysis.id}
                  checked={isSelected}
                  onChange={() => handleCheckboxChange(analysis)}
                  className="checkbox"
                />
                <label htmlFor={analysis.id} className="checkbox-label">
                  <h3>{analysis.icon} {analysis.name}</h3>
                </label>
              </div>
              <p>{analysis.description}</p>
              <p><strong>Complexity:</strong> {analysis.complexity}</p>
            </div>
          );
        })}
      </div>

      <div className="card" style={{ marginTop: '20px', textAlign: 'center' }}>
        <p><strong>Selected Analyses:</strong> {selectedAnalyses.length}</p>
        {selectedAnalyses.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            {selectedAnalyses.map(analysis => (
              <span key={analysis.id} className="selected-tag">
                {analysis.icon} {analysis.name}
              </span>
            ))}
          </div>
        )}
        <button 
          className="button" 
          onClick={handleContinue}
          disabled={selectedAnalyses.length === 0}
        >
          Continue with Selected Analyses ({selectedAnalyses.length})
        </button>
      </div>
    </div>
  );
}

export default AnalysisSelection; 