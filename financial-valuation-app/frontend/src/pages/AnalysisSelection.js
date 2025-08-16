import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Calculator, BarChart3, TrendingUp, CheckCircle, ArrowRight, Loader2, AlertCircle } from 'lucide-react';

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
    
    const analysisIds = selectedAnalyses.map(a => a.id).join(',');
    localStorage.setItem('selectedAnalysisTypes', JSON.stringify(selectedAnalyses));
    navigate(`/analysis/${analysisIds}`);
  };

  if (loading) {
    return (
      <div className="container-modern">
        <div className="card-elevated text-center">
          <div className="flex justify-center mb-4">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Analysis Types</h2>
          <p className="text-gray-600">Please wait while we prepare your valuation options...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-modern">
        <div className="card-elevated text-center">
          <div className="flex justify-center mb-4">
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Analysis Types</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button className="btn btn-primary" onClick={fetchAnalysisTypes}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container-modern">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <TrendingUp className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Financial Valuation Analysis
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Select one or more analysis types to begin your comprehensive financial valuation
        </p>
      </div>
      
      {/* Analysis Grid */}
      <div className="grid-cards mb-12">
        {analysisTypes.map((analysis) => {
          const isSelected = selectedAnalyses.find(item => item.id === analysis.id);
          return (
            <div 
              key={analysis.id} 
              className={`card cursor-pointer transition-all duration-200 ${
                isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
              }`}
              onClick={() => handleCheckboxChange(analysis)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    isSelected ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    <Calculator className={`h-5 w-5 ${
                      isSelected ? 'text-blue-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{analysis.name}</h3>
                    <p className="text-sm text-gray-500">{analysis.complexity} complexity</p>
                  </div>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  isSelected 
                    ? 'border-blue-500 bg-blue-500' 
                    : 'border-gray-300'
                }`}>
                  {isSelected && <CheckCircle className="h-3 w-3 text-white" />}
                </div>
              </div>
              
              <p className="text-gray-600 text-sm mb-4">
                {analysis.description}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    analysis.complexity === 'High' ? 'bg-red-500' :
                    analysis.complexity === 'Medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}></div>
                  <span className="text-xs text-gray-500">
                    {analysis.complexity} Level
                  </span>
                </div>
                {isSelected && (
                  <div className="flex items-center space-x-1 text-blue-600 text-sm font-medium">
                    <span>Selected</span>
                    <CheckCircle className="h-4 w-4" />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary & Continue */}
      <div className="card-elevated text-center">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          Analysis Selection Summary
        </h3>
        
        {selectedAnalyses.length > 0 ? (
          <div className="space-y-6">
            <div className="flex flex-wrap justify-center gap-2">
              {selectedAnalyses.map(analysis => (
                <div key={analysis.id} className="status-badge status-info">
                  <Calculator className="h-4 w-4" />
                  {analysis.name}
                </div>
              ))}
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-blue-800 font-medium">
                <span className="font-semibold">{selectedAnalyses.length}</span> analysis type{selectedAnalyses.length !== 1 ? 's' : ''} selected
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <p className="text-yellow-800">
              Please select at least one analysis type to continue
            </p>
          </div>
        )}
        
        <div className="mt-8">
          <button 
            className={`btn btn-primary text-lg px-8 py-4 ${
              selectedAnalyses.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={handleContinue}
            disabled={selectedAnalyses.length === 0}
          >
            <span>Continue with Selected Analyses</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AnalysisSelection; 