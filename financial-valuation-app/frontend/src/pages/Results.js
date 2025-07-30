import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { DCFChart, MonteCarloChart, SensitivityChart } from '../components/Charts';

function Results() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [allResults, setAllResults] = useState([]);
  const [analysisTypes, setAnalysisTypes] = useState([]);
  const [selectedAnalysisIds, setSelectedAnalysisIds] = useState([]);
  const [selectedAnalysisTypes, setSelectedAnalysisTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [analysisId]);

  const fetchResults = async () => {
    try {
      // Parse multiple analysis IDs
      const analysisIds = analysisId.split(',');
      setSelectedAnalysisIds(analysisIds);

      // Fetch analysis types to get names
      const typesResponse = await axios.get('/api/analysis/types');
      const allTypes = typesResponse.data;

      // Get selected analysis types from localStorage
      const storedSelectedTypes = localStorage.getItem('selectedAnalysisTypes');
      let selectedTypes = [];
      if (storedSelectedTypes) {
        try {
          const parsed = JSON.parse(storedSelectedTypes);
          selectedTypes = parsed.map(analysis => analysis.id);
          setSelectedAnalysisTypes(selectedTypes);
        } catch (err) {
          console.error('Error parsing stored analysis types:', err);
        }
      }

      // Fetch results for each analysis
      const resultsPromises = analysisIds.map(async (id) => {
        try {
          const response = await axios.get(`/api/results/${id}/results`);
          return response.data;
        } catch (err) {
          console.error(`Error fetching results for ${id}:`, err);
          return null;
        }
      });

      const results = await Promise.all(resultsPromises);
      const validResults = results.filter(result => result !== null);

      setAllResults(validResults);
      setAnalysisTypes(allTypes);
      setLoading(false);

      // Debug logging
      console.log('Analysis IDs from URL:', analysisIds);
      console.log('Selected Analysis IDs:', selectedAnalysisIds);
      console.log('Selected Analysis Types:', selectedTypes);
      console.log('All Results:', validResults);
      console.log('First Result Structure:', validResults[0] ? Object.keys(validResults[0]) : 'No results');
    } catch (err) {
      setError('Failed to load results');
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getAnalysisName = (analysisTypeId) => {
    const analysis = analysisTypes.find(type => type.id === analysisTypeId);
    return analysis ? analysis.name : analysisTypeId;
  };

  const wasAnalysisSelected = (analysisTypeId) => {
    const isSelected = selectedAnalysisTypes.includes(analysisTypeId);
    console.log(`Checking if ${analysisTypeId} was selected:`, isSelected, 'Selected Types:', selectedAnalysisTypes);
    return isSelected;
  };

  const renderDCFResults = (results) => {
    if (!results.dcf_valuation) return null;

    const dcf = results.dcf_valuation;
    return (
      <div className="card" style={{ marginBottom: '30px' }}>
        <h2 style={{ borderBottom: '2px solid #007bff', paddingBottom: '10px', marginBottom: '20px' }}>
          📊 DCF Valuation (WACC)
        </h2>

        <div className="grid">
          <div className="card">
            <h3>Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(dcf.enterprise_value)}
            </p>
          </div>
          <div className="card">
            <h3>Equity Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(dcf.equity_value)}
            </p>
          </div>
          <div className="card">
            <h3>Price per Share</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
              ${dcf.price_per_share}
            </p>
          </div>
        </div>

        <div className="grid" style={{ marginTop: '20px' }}>
          <div className="card">
            <h3>WACC</h3>
            <p>{formatPercentage(dcf.wacc)}</p>
          </div>
          <div className="card">
            <h3>Terminal Growth</h3>
            <p>{formatPercentage(dcf.terminal_growth)}</p>
          </div>
          <div className="card">
            <h3>Terminal Value</h3>
            <p>{formatCurrency(dcf.terminal_value)}</p>
          </div>
          <div className="card">
            <h3>Present Value of FCFs</h3>
            <p>{formatCurrency(dcf.present_value_of_fcfs)}</p>
          </div>
        </div>

        {dcf.free_cash_flows_after_tax_fcff && (
          <div className="card">
            <h3>Free Cash Flows (5 Years)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
              {dcf.free_cash_flows_after_tax_fcff.map((fcf, index) => (
                <div key={index} style={{ textAlign: 'center' }}>
                  <strong>Year {index + 1}</strong>
                  <p>{formatCurrency(fcf)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        <div style={{ marginTop: '30px' }}>
          <h3>Free Cash Flows (Chart)</h3>
          <DCFChart data={dcf} />
        </div>
      </div>
    );
  };

  const renderAPVResults = (results) => {
    if (!results.apv_valuation) return null;

    const apv = results.apv_valuation;
    return (
      <div className="card" style={{ marginBottom: '30px' }}>
        <h2 style={{ borderBottom: '2px solid #28a745', paddingBottom: '10px', marginBottom: '20px' }}>
          💰 APV Valuation
        </h2>

        <div className="grid">
          <div className="card">
            <h3>Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(apv.enterprise_value)}
            </p>
          </div>
          <div className="card">
            <h3>Equity Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(apv.equity_value)}
            </p>
          </div>
          <div className="card">
            <h3>Price per Share</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
              ${apv.price_per_share}
            </p>
          </div>
        </div>

        <div className="grid" style={{ marginTop: '20px' }}>
          <div className="card">
            <h3>Unlevered Cost of Equity</h3>
            <p>{formatPercentage(apv.unlevered_cost_of_equity)}</p>
          </div>
          <div className="card">
            <h3>Value Unlevered</h3>
            <p>{formatCurrency(apv.apv_components.value_unlevered)}</p>
          </div>
          <div className="card">
            <h3>PV Tax Shield</h3>
            <p>{formatCurrency(apv.apv_components.pv_tax_shield)}</p>
          </div>
        </div>
      </div>
    );
  };

  const renderComparableResults = (results) => {
    if (!results.comparable_valuation) return null;

    const comp = results.comparable_valuation;
    return (
      <div className="card" style={{ marginBottom: '30px' }}>
        <h2 style={{ borderBottom: '2px solid #ffc107', paddingBottom: '10px', marginBottom: '20px' }}>
          📈 Comparable Multiples
        </h2>

        <div className="grid">
          <div className="card">
            <h3>Mean Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(comp.ev_multiples.mean_ev)}
            </p>
          </div>
          <div className="card">
            <h3>Median Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(comp.ev_multiples.median_ev)}
            </p>
          </div>
          <div className="card">
            <h3>Standard Deviation</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
              {formatCurrency(comp.ev_multiples.std_dev)}
            </p>
          </div>
        </div>

        <div className="card">
          <h3>Implied Values by Multiple</h3>
          <div className="grid">
            {Object.entries(comp.implied_evs_by_multiple).map(([multiple, data]) => (
              <div key={multiple} className="card">
                <h4>{multiple}</h4>
                <p><strong>Mean Implied EV:</strong> {formatCurrency(data.mean_implied_ev)}</p>
                <p><strong>Median Implied EV:</strong> {formatCurrency(data.median_implied_ev)}</p>
                <p><strong>Mean Multiple:</strong> {data.mean_multiple.toFixed(2)}x</p>
                <p><strong>Peer Count:</strong> {data.peer_count}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderScenarioResults = (results) => {
    if (!results.scenarios) return null;

    return (
      <div className="card" style={{ marginBottom: '30px' }}>
        <h2 style={{ borderBottom: '2px solid #17a2b8', paddingBottom: '10px', marginBottom: '20px' }}>
          🎯 Scenario Analysis
        </h2>

        <div className="grid">
          {Object.entries(results.scenarios).map(([scenario, data]) => (
            <div key={scenario} className="card">
              <h3 style={{ textTransform: 'capitalize' }}>{scenario.replace('_', ' ')}</h3>
              <p><strong>Enterprise Value:</strong> {formatCurrency(data.ev)}</p>
              <p><strong>Equity Value:</strong> {formatCurrency(data.equity)}</p>
              <p><strong>Price per Share:</strong> ${data.price_per_share}</p>
              {data.input_changes && (
                <div style={{ marginTop: '10px', padding: '10px', background: '#f8f9fa', borderRadius: '4px' }}>
                  <strong>Input Changes:</strong>
                  {Object.entries(data.input_changes).map(([key, value]) => (
                    <p key={key} style={{ margin: '2px 0', fontSize: '14px' }}>
                      {key}: {Array.isArray(value) ? value.join(', ') : value}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSensitivityResults = (results) => {
    if (!results.sensitivity_analysis) return null;

    const sens = results.sensitivity_analysis;
    return (
      <div className="card" style={{ marginBottom: '30px', borderLeft: '5px solid #fd7e14' }}>
        <h2 style={{ borderBottom: '2px solid #fd7e14', paddingBottom: '10px', marginBottom: '20px' }}>
          📉 Sensitivity Analysis
        </h2>

        {Object.entries(sens).map(([parameter, data]) => (
          <div key={parameter} className="card" style={{ marginBottom: '20px' }}>
            <h3 style={{ textTransform: 'capitalize' }}>{parameter.replace('_', ' ')}</h3>
            <div className="grid">
              <div className="card">
                <h4>Enterprise Value</h4>
                {Object.entries(data.ev).map(([value, ev]) => (
                  <p key={value} style={{ margin: '2px 0' }}>
                    {value}: {formatCurrency(ev)}
                  </p>
                ))}
              </div>
              <div className="card">
                <h4>Price per Share</h4>
                {Object.entries(data.price_per_share).map(([value, price]) => (
                  <p key={value} style={{ margin: '2px 0' }}>
                    {value}: ${price}
                  </p>
                ))}
              </div>
            </div>
          </div>
        ))}
        <div style={{ marginTop: '30px' }}>
          <h3>Enterprise Value Sensitivity (Chart)</h3>
          <SensitivityChart data={sens} />
        </div>
      </div>
    );
  };

  const renderMonteCarloResults = (results) => {
    if (!results.monte_carlo_simulation) return null;

    const mc = results.monte_carlo_simulation;
    return (
      <div className="card" style={{ marginBottom: '30px', borderLeft: '5px solid #6f42c1' }}>
        <h2 style={{ borderBottom: '2px solid #6f42c1', paddingBottom: '10px', marginBottom: '20px' }}>
          🎲 Monte Carlo Simulation
        </h2>

        <div className="grid">
          <div className="card">
            <h3>Mean Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(mc.wacc_method.mean_ev)}
            </p>
          </div>
          <div className="card">
            <h3>Median Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(mc.wacc_method.median_ev)}
            </p>
          </div>
          <div className="card">
            <h3>Standard Deviation</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
              {formatCurrency(mc.wacc_method.std_dev)}
            </p>
          </div>
        </div>

        <div className="card">
          <h3>95% Confidence Interval</h3>
          <p style={{ fontSize: '18px', textAlign: 'center' }}>
            {formatCurrency(mc.wacc_method.confidence_interval_95[0])} - {formatCurrency(mc.wacc_method.confidence_interval_95[1])}
          </p>
        </div>

        <div className="card">
          <p><strong>Simulation Runs:</strong> {mc.runs.toLocaleString()}</p>
        </div>
        <div style={{ marginTop: '30px' }}>
          <h3>Monte Carlo Distribution (Chart)</h3>
          <MonteCarloChart data={mc} />
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h2>Loading results...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h2>Error: {error}</h2>
          <button className="button" onClick={fetchResults}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!allResults || allResults.length === 0) {
    return (
      <div className="container">
        <div className="card">
          <h2>No results found</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Financial Valuation Results</h1>

      {/* Show only the analysis types that were selected by the user */}
      {allResults.length > 0 && (
        <div>
          {/* DCF Results - only if selected */}
          {wasAnalysisSelected('dcf_wacc') && renderDCFResults(allResults[0])}

          {/* APV Results - only if selected */}
          {wasAnalysisSelected('apv') && renderAPVResults(allResults[0])}

          {/* Comparable Multiples Results - only if selected */}
          {wasAnalysisSelected('multiples') && renderComparableResults(allResults[0])}

          {/* Scenario Analysis Results - only if selected */}
          {wasAnalysisSelected('scenario') && renderScenarioResults(allResults[0])}

          {/* Sensitivity Analysis Results - only if selected */}
          {wasAnalysisSelected('sensitivity') && renderSensitivityResults(allResults[0])}

          {/* Monte Carlo Results - only if selected */}
          {wasAnalysisSelected('monte_carlo') && renderMonteCarloResults(allResults[0])}
        </div>
      )}



      <div className="card">
        <button className="button" onClick={() => navigate('/')}>
          Start New Analysis
        </button>
      </div>
    </div>
  );
}

export default Results; 