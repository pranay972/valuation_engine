import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { APVChart, ComparableMultiplesChart, DCFChart, MonteCarloChart, ScenarioChart, SensitivityChart } from '../components/Charts';
import { analysisAPI, resultsAPI } from '../services/api';

function Results() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [allResults, setAllResults] = useState([]);
  const [analysisTypes, setAnalysisTypes] = useState([]);
  const [selectedAnalysisIds, setSelectedAnalysisIds] = useState([]);
  const [selectedAnalysisTypes, setSelectedAnalysisTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState({});
  const [isPolling, setIsPolling] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState(new Date());
  const pollingIntervalRef = useRef(null);

  // Simple polling - just hit the API every 2 seconds
  useEffect(() => {
    if (selectedAnalysisIds.length === 0) return;

    // Start polling
    setIsPolling(true);
    pollingIntervalRef.current = setInterval(() => {
      fetchResults();
    }, 2000);

    // Cleanup
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [selectedAnalysisIds]);

  const fetchResults = async () => {
    try {
      // Parse multiple analysis IDs
      const analysisIds = analysisId.split(',');
      setSelectedAnalysisIds(analysisIds);

      // Fetch analysis types
      const typesResponse = await analysisAPI.getAnalysisTypes();
      const allTypes = typesResponse.data.data;
      setAnalysisTypes(allTypes);

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

      // Check status for each analysis
      const statusPromises = analysisIds.map(async (id) => {
        try {
          const response = await resultsAPI.getStatus(id);
          return { id, status: response.data.data };
        } catch (err) {
          console.error(`Error fetching status for ${id}:`, err);
          return { id, status: null };
        }
      });

      const statuses = await Promise.all(statusPromises);
      const statusMap = {};
      statuses.forEach(({ id, status }) => {
        if (status) statusMap[id] = status;
      });
      setAnalysisStatus(statusMap);

      // Fetch results for each analysis
      const resultsPromises = analysisIds.map(async (id) => {
        try {
          const response = await resultsAPI.getResults(id);
          return response.data;
        } catch (err) {
          console.error(`Error fetching results for ${id}:`, err);
          return null;
        }
      });

      const results = await Promise.all(resultsPromises);
      const validResults = results.filter(result => result !== null);

      setAllResults(validResults);
      setLoading(false);

      // Stop polling if all analyses are complete
      const allComplete = Object.values(statusMap).every(status =>
        status.status === 'completed' || status.status === 'failed'
      );

      if (allComplete) {
        setIsPolling(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }

    } catch (err) {
      setError('Failed to load results');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, [analysisId]);

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
    // First check if it was explicitly selected from localStorage
    const isSelected = selectedAnalysisTypes.includes(analysisTypeId);

    // If no explicit selection, check if we have results for this analysis type
    if (!isSelected && allResults.length > 0) {
      const result = allResults[0];
      if (result.data && result.data.results && result.data.results.results_data) {
        const resultsData = result.data.results.results_data;
        // Check if this analysis type has results
        if (resultsData[analysisTypeId]) {
          return true;
        }
      }
    }

    return isSelected;
  };

  const findResultByAnalysisType = (analysisTypeId) => {
    // Find the result that has this specific analysis type
    for (const result of allResults) {
      if (result.data && result.data.analysis && result.data.analysis.analysis_type === analysisTypeId) {
        return result;
      }
    }
    // Fallback to first result if no specific match found
    return allResults[0];
  };

  const renderDCFResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both dcf_valuation (new) and dcf_wacc (legacy)
    const dcf = resultsData?.dcf_valuation || resultsData?.dcf_wacc;
    if (!dcf) {
      return null;
    }

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
            <h3>Price Per Share</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
              {formatCurrency(dcf.price_per_share)}
            </p>
          </div>
        </div>

        <div className="grid">
          <div className="card">
            <h3>WACC</h3>
            <p style={{ fontSize: '20px', color: '#6c757d' }}>
              {formatPercentage(dcf.wacc)}
            </p>
          </div>
          <div className="card">
            <h3>Terminal Growth</h3>
            <p style={{ fontSize: '20px', color: '#6c757d' }}>
              {formatPercentage(dcf.terminal_growth)}
            </p>
          </div>
          <div className="card">
            <h3>Terminal Value</h3>
            <p style={{ fontSize: '20px', color: '#6c757d' }}>
              {formatCurrency(dcf.terminal_value)}
            </p>
          </div>
        </div>

        {dcf.net_debt_breakdown && (
          <div className="card">
            <h3>Net Debt Breakdown</h3>
            <div className="grid">
              <div>
                <strong>Current Debt:</strong> {formatCurrency(dcf.net_debt_breakdown.current_debt)}
              </div>
              <div>
                <strong>Cash Balance:</strong> {formatCurrency(dcf.net_debt_breakdown.cash_balance)}
              </div>
              <div>
                <strong>Net Debt:</strong> {formatCurrency(dcf.net_debt_breakdown.net_debt)}
              </div>
            </div>
          </div>
        )}

        {dcf.wacc_components && (
          <div className="card">
            <h3>WACC Components</h3>
            <div className="grid">
              <div>
                <strong>Cost of Equity:</strong> {formatPercentage(dcf.wacc_components.cost_of_equity)}
              </div>
              <div>
                <strong>Cost of Debt:</strong> {formatPercentage(dcf.wacc_components.cost_of_debt)}
              </div>
              <div>
                <strong>Target Debt Ratio:</strong> {formatPercentage(dcf.wacc_components.target_debt_ratio)}
              </div>
              <div>
                <strong>Tax Rate:</strong> {formatPercentage(dcf.wacc_components.tax_rate)}
              </div>
            </div>
          </div>
        )}

        {dcf.free_cash_flows_after_tax_fcff && (
          <div className="card">
            <h3>Free Cash Flows (FCFF)</h3>
            <div className="grid">
              {dcf.free_cash_flows_after_tax_fcff.map((fcf, index) => (
                <div key={index}>
                  <strong>Year {index + 1}:</strong> {formatCurrency(fcf)}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DCF Chart */}
        <div className="card">
          <h3>Free Cash Flows Chart</h3>
          <DCFChart data={dcf} />
        </div>
      </div>
    );
  };

  const renderAPVResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both apv_valuation (new) and apv (legacy)
    const apv = resultsData?.apv_valuation || resultsData?.apv;
    if (!apv) return null;

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
            <h3>Price Per Share</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
              {formatCurrency(apv.price_per_share)}
            </p>
          </div>
        </div>

        {apv.apv_components && (
          <div className="card">
            <h3>APV Components</h3>
            <div className="grid">
              <div>
                <strong>Value Unlevered:</strong> {formatCurrency(apv.apv_components.value_unlevered)}
              </div>
              <div>
                <strong>PV Tax Shield:</strong> {formatCurrency(apv.apv_components.pv_tax_shield)}
              </div>
            </div>
          </div>
        )}

        {apv.net_debt_breakdown && (
          <div className="card">
            <h3>Net Debt Breakdown</h3>
            <div className="grid">
              <div>
                <strong>Current Debt:</strong> {formatCurrency(apv.net_debt_breakdown.current_debt)}
              </div>
              <div>
                <strong>Cash Balance:</strong> {formatCurrency(apv.net_debt_breakdown.cash_balance)}
              </div>
              <div>
                <strong>Net Debt:</strong> {formatCurrency(apv.net_debt_breakdown.net_debt)}
              </div>
            </div>
          </div>
        )}

        {apv.unlevered_fcfs_used && (
          <div className="card">
            <h3>Unlevered Free Cash Flows</h3>
            <div className="grid">
              {apv.unlevered_fcfs_used.map((fcf, index) => (
                <div key={index}>
                  <strong>Year {index + 1}:</strong> {formatCurrency(fcf)}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* APV Chart */}
        <div className="card">
          <h3>Unlevered Free Cash Flows Chart</h3>
          <APVChart data={apv} />
        </div>
      </div>
    );
  };

  const renderComparableResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both comparable_valuation (new) and comparable_multiples (legacy)
    const comp = resultsData?.comparable_valuation || resultsData?.comparable_multiples;
    if (!comp) return null;

    return (
      <div className="card" style={{ marginBottom: '30px' }}>
        <h2 style={{ borderBottom: '2px solid #ffc107', paddingBottom: '10px', marginBottom: '20px' }}>
          📈 Comparable Multiples
        </h2>

        {/* Summary Values */}
        <div className="grid" style={{ marginBottom: '30px' }}>
          <div className="card">
            <h3>Enterprise Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(comp.enterprise_value)}
            </p>
          </div>
          <div className="card">
            <h3>Equity Value</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(comp.equity_value)}
            </p>
          </div>
          <div className="card">
            <h3>Price Per Share</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
              {formatCurrency(comp.price_per_share)}
            </p>
          </div>
        </div>

        {comp.ev_multiples && (
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
        )}

        {comp.implied_evs_by_multiple && (
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
        )}

        {/* Comparable Multiples Chart */}
        <div className="card">
          <h3>Implied Values by Multiple (Chart)</h3>
          <ComparableMultiplesChart data={comp} />
        </div>
      </div>
    );
  };

  const renderScenarioResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both scenarios (new) and scenario (legacy)
    const scenarios = resultsData?.scenarios || resultsData?.scenario;
    if (!scenarios) return null;

    // The scenarios data might be nested under resultsData.scenarios.scenarios
    const scenarioData = scenarios.scenarios || scenarios;
    if (!scenarioData) return null;

    return (
      <div className="card" style={{ marginBottom: '30px', borderLeft: '5px solid #17a2b8' }}>
        <h2 style={{ borderBottom: '2px solid #17a2b8', paddingBottom: '10px', marginBottom: '20px' }}>
          🎯 Scenario Analysis
        </h2>

        {/* Detailed Scenario Breakdown */}
        <div className="grid">
          {Object.entries(scenarioData).map(([scenario, data]) => (
            <div key={scenario} className="card">
              <h3 style={{ textTransform: 'capitalize', color: scenario === 'Base Case' ? '#17a2b8' : scenario === 'Optimistic' ? '#28a745' : '#dc3545' }}>
                {scenario.replace('_', ' ')}
              </h3>
              <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '15px' }}>
                <p style={{ color: '#007bff' }}><strong>Enterprise Value:</strong> {formatCurrency(data.ev)}</p>
                <p style={{ color: '#28a745' }}><strong>Equity Value:</strong> {formatCurrency(data.equity)}</p>
                <p style={{ color: '#fd7e14' }}><strong>Price per Share:</strong> {formatCurrency(data.price_per_share)}</p>
              </div>
              {data.input_changes && (
                <div style={{ marginTop: '15px', padding: '15px', background: '#f8f9fa', borderRadius: '8px', border: '1px solid #e9ecef' }}>
                  <strong style={{ color: '#6c757d' }}>Input Changes:</strong>
                  {Object.entries(data.input_changes).map(([key, value]) => (
                    <p key={key} style={{ margin: '8px 0', fontSize: '14px', color: '#495057' }}>
                      <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {Array.isArray(value) ? value.join(', ') : value}
                    </p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Scenario Chart */}
        <div className="card">
          <h3>Scenario Comparison Chart</h3>
          <ScenarioChart data={scenarioData} />
        </div>
      </div>
    );
  };

  const renderSensitivityResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both sensitivity_analysis (new) and sensitivity (legacy)
    const sens = resultsData?.sensitivity_analysis || resultsData?.sensitivity;
    if (!sens) return null;

    const sensitivityResults = sens.sensitivity_results;

    if (!sensitivityResults) return null;

    return (
      <div className="card" style={{ marginBottom: '30px', borderLeft: '5px solid #fd7e14' }}>
        <h2 style={{ borderBottom: '2px solid #fd7e14', paddingBottom: '10px', marginBottom: '20px' }}>
          📉 Sensitivity Analysis
        </h2>

        {Object.entries(sensitivityResults).map(([parameter, data]) => (
          <div key={parameter} className="card" style={{ marginBottom: '20px' }}>
            <h3 style={{ textTransform: 'capitalize' }}>{parameter.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
            <div className="grid">
              <div className="card">
                <h4>Enterprise Value</h4>
                {Object.entries(data.ev || {}).map(([value, ev]) => (
                  <p key={value} style={{ margin: '2px 0' }}>
                    {value}: {formatCurrency(ev)}
                  </p>
                ))}
              </div>
              <div className="card">
                <h4>Price per Share</h4>
                {Object.entries(data.price_per_share || {}).map(([value, price]) => (
                  <p key={value} style={{ margin: '2px 0' }}>
                    {value}: {formatCurrency(price)}
                  </p>
                ))}
              </div>
            </div>
          </div>
        ))}
        <div style={{ marginTop: '30px' }}>
          <h3>Enterprise Value Sensitivity (Chart)</h3>
          <SensitivityChart data={sensitivityResults} />
        </div>
      </div>
    );
  };

  const renderMonteCarloResults = (results) => {
    // Extract the actual results data from the nested structure
    const resultsData = results?.data?.results?.results_data;

    // Check for both monte_carlo_simulation (new) and monte_carlo (legacy)
    const mc = resultsData?.monte_carlo_simulation || resultsData?.monte_carlo;
    if (!mc) return null;

    return (
      <div className="card" style={{ marginBottom: '30px', borderLeft: '5px solid #6f42c1' }}>
        <h2 style={{ borderBottom: '2px solid #6f42c1', paddingBottom: '10px', marginBottom: '20px' }}>
          🎲 Monte Carlo Simulation
        </h2>

        {mc.wacc_method && (
          <>
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
          </>
        )}

        {mc.runs && (
          <div className="card">
            <p><strong>Simulation Runs:</strong> {mc.runs.toLocaleString()}</p>
          </div>
        )}

        <div style={{ marginTop: '30px' }}>
          <h3>Monte Carlo Distribution (Chart)</h3>
          <MonteCarloChart data={mc} />
        </div>
      </div>
    );
  };

  const renderSpinner = () => (
    <div className="container">
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <div className="spinner" style={{
          width: '50px',
          height: '50px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }}></div>
        <h2>Processing Analysis...</h2>
        <p>Your financial valuation is being calculated. This may take a few moments.</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );

  const renderProcessingStatus = () => (
    <div className="container">
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ marginBottom: '20px' }}>
          <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
          <h2>Analysis in Progress</h2>
          <p>Your financial analysis is being processed. This may take a few minutes.</p>
        </div>

        <div style={{ marginTop: '20px', fontSize: '14px', color: '#6c757d' }}>
          <p>🔄 Auto-refreshing every 2 seconds...</p>
          <p>Last update: {lastUpdateTime.toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return renderSpinner();
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

  // Check if any analysis is still processing
  const hasProcessingAnalyses = Object.values(analysisStatus).some(status =>
    status.status === 'processing' || status.status === 'pending'
  );

  if (hasProcessingAnalyses) {
    return renderProcessingStatus();
  }

  if (!allResults || allResults.length === 0) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <h2>No Results Available</h2>
          <p>It looks like the analysis hasn't completed yet or there was an issue processing your inputs.</p>
          <div style={{ marginTop: '20px' }}>
            <button className="button" onClick={fetchResults}>
              Check Again
            </button>
            <button className="button" onClick={() => navigate('/')} style={{ marginLeft: '10px' }}>
              Start New Analysis
            </button>
          </div>
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
          {wasAnalysisSelected('dcf_wacc') && renderDCFResults(findResultByAnalysisType('dcf_wacc'))}

          {/* APV Results - only if selected */}
          {wasAnalysisSelected('apv') && renderAPVResults(findResultByAnalysisType('apv'))}

          {/* Comparable Multiples Results - only if selected */}
          {wasAnalysisSelected('multiples') && renderComparableResults(findResultByAnalysisType('multiples'))}

          {/* Scenario Analysis Results - only if selected */}
          {wasAnalysisSelected('scenario') && renderScenarioResults(findResultByAnalysisType('scenario'))}

          {/* Sensitivity Analysis Results - only if selected */}
          {wasAnalysisSelected('sensitivity') && renderSensitivityResults(findResultByAnalysisType('sensitivity'))}

          {/* Monte Carlo Results - only if selected */}
          {wasAnalysisSelected('monte_carlo') && renderMonteCarloResults(findResultByAnalysisType('monte_carlo'))}
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