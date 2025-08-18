import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CSVUpload } from '../components/CSVUpload';
import { analysisAPI, valuationAPI } from '../services/api';

function InputForm() {
  const { analysisType } = useParams();
  const navigate = useNavigate();
  const [selectedAnalyses, setSelectedAnalyses] = useState([]);
  const [selectedAnalysisTypeIds, setSelectedAnalysisTypeIds] = useState([]);
  const [formData, setFormData] = useState({
    // Company Information
    company_name: '',
    valuation_date: new Date().toISOString().split('T')[0],
    forecast_years: 5,

    // Core Financial Inputs - EXACTLY matching sample_input.json
    revenue: [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    ebit_margin: 0.18,
    tax_rate: 0.25,
    capex: [187.5, 206.3, 226.9, 249.6, 274.5],
    depreciation: [125.0, 137.5, 151.3, 166.4, 183.0],
    nwc_changes: [-25.0, -27.5, -30.3, -33.3, -36.6],
    weighted_average_cost_of_capital: 0.095,
    terminal_growth_rate: 0.025,
    share_count: 45.2,
    cost_of_debt: 0.065,
    cash_balance: 50.0,

    // Cost of Capital - EXACTLY matching sample_input.json structure
    cost_of_capital: {
      risk_free_rate: 0.03,
      market_risk_premium: 0.06,
      levered_beta: 1.2,
      unlevered_beta: 1.2,
      target_debt_to_value_ratio: 0.3,
      unlevered_cost_of_equity: 0.0,
      cost_of_equity: 0.14
    },

    // Debt Schedule - EXACTLY matching sample_input.json
    debt_schedule: {
      "0": 150.0
    },

    // Control flags - EXACTLY matching sample_input.json
    use_input_wacc: true,
    use_debt_schedule: false,

    // Comparable Multiples - EXACTLY matching sample_input.json
    comparable_multiples: {
      "EV/EBITDA": [12.5, 14.2, 13.8, 15.1, 13.9],
      "EV/Revenue": [2.8, 3.1, 2.9, 3.3, 3.0],
      "P/E": [18.5, 22.1, 20.8, 24.3, 21.4]
    },

    // Sensitivity Analysis - EXACTLY matching sample_input.json
    sensitivity_analysis: {
      ebit_margin: [0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21],
      terminal_growth_rate: [0.02, 0.0225, 0.025, 0.0275, 0.03],
      weighted_average_cost_of_capital: [0.085, 0.09, 0.095, 0.10, 0.105]
    },

    // Monte Carlo Specs - EXACTLY matching sample_input.json
    monte_carlo_specs: {
      ebit_margin: {
        distribution: "normal",
        params: {
          mean: 0.18,
          std: 0.02
        }
      },
      terminal_growth_rate: {
        distribution: "normal",
        params: {
          mean: 0.025,
          std: 0.005
        }
      },
      weighted_average_cost_of_capital: {
        distribution: "normal",
        params: {
          mean: 0.095,
          std: 0.01
        }
      }
    },

    // Scenario Definitions - EXACTLY matching sample_input.json
    scenarios: {
      "optimistic": {
        ebit_margin: 0.22,
        terminal_growth_rate: 0.035,
        weighted_average_cost_of_capital: 0.085
      },
      "pessimistic": {
        ebit_margin: 0.14,
        terminal_growth_rate: 0.015,
        weighted_average_cost_of_capital: 0.105
      }
    }
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (analysisType) {
      const analysisIds = analysisType.split(',');
      setSelectedAnalysisTypeIds(analysisIds);
      fetchAnalysisTypes(analysisIds);
    }
  }, [analysisType]);

  const fetchAnalysisTypes = async (analysisIds) => {
    try {
      const response = await analysisAPI.getAnalysisTypes();
      const allAnalyses = response.data.data;
      const selected = allAnalyses.filter(analysis =>
        analysisIds.includes(analysis.id)
      );
      setSelectedAnalyses(selected);
    } catch (error) {
      console.error('Error fetching analysis types:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // Handle nested cost_of_capital fields
    if (name.startsWith('cost_of_capital.')) {
      const field = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        cost_of_capital: {
          ...prev.cost_of_capital,
          [field]: parseFloat(value) || 0
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleArrayInputChange = (fieldName, index, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: prev[fieldName].map((item, i) => i === index ? parseFloat(value) || 0 : item)
    }));
  };

  // Add this handler to update formData from CSV
  const handleCSVData = (csvData) => {
    setFormData(prev => ({
      ...prev,
      ...csvData
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Create analyses for each selected type
      const analysisPromises = selectedAnalyses.map(analysis =>
        analysisAPI.createAnalysis({
          analysis_type: analysis.id,
          company_name: formData.company_name
        })
      );

      const analysisResponses = await Promise.all(analysisPromises);
      const analysisIds = analysisResponses.map(response => response.data.data.id);

      // Prepare the complete input data - EXACTLY matching sample_input.json structure
      const completeInputData = {
        company_name: formData.company_name,
        valuation_date: formData.valuation_date,
        forecast_years: parseInt(formData.forecast_years),
        financial_inputs: {
          revenue: formData.revenue,
          ebit_margin: parseFloat(formData.ebit_margin) || 0,
          tax_rate: parseFloat(formData.tax_rate) || 0,
          capex: formData.capex,
          depreciation: formData.depreciation,
          nwc_changes: formData.nwc_changes,
          weighted_average_cost_of_capital: parseFloat(formData.weighted_average_cost_of_capital) || 0,
          terminal_growth_rate: parseFloat(formData.terminal_growth_rate) || 0,
          share_count: parseFloat(formData.share_count) || 0,
          cost_of_debt: parseFloat(formData.cost_of_debt) || 0,
          cash_balance: parseFloat(formData.cash_balance) || 0,
          cost_of_capital: {
            risk_free_rate: parseFloat(formData.cost_of_capital.risk_free_rate) || 0,
            market_risk_premium: parseFloat(formData.cost_of_capital.market_risk_premium) || 0,
            levered_beta: parseFloat(formData.cost_of_capital.levered_beta) || 0,
            unlevered_beta: parseFloat(formData.cost_of_capital.unlevered_beta) || 0,
            target_debt_to_value_ratio: parseFloat(formData.cost_of_capital.target_debt_to_value_ratio) || 0,
            unlevered_cost_of_equity: parseFloat(formData.cost_of_capital.unlevered_cost_of_equity) || 0,
            cost_of_equity: parseFloat(formData.cost_of_capital.cost_of_equity) || 0
          },
          debt_schedule: formData.debt_schedule,
          use_input_wacc: formData.use_input_wacc,
          use_debt_schedule: formData.use_debt_schedule
        },
        comparable_multiples: formData.comparable_multiples,
        sensitivity_analysis: formData.sensitivity_analysis,
        monte_carlo_specs: formData.monte_carlo_specs,
        scenarios: formData.scenarios
      };

      // Debug: Log the complete input data to check for any undefined values
      console.log('Complete input data:', JSON.stringify(completeInputData, null, 2));

      // Check for any undefined or null values
      const checkForUndefined = (obj, path = '') => {
        for (const [key, value] of Object.entries(obj)) {
          const currentPath = path ? `${path}.${key}` : key;
          if (value === undefined || value === null) {
            console.error(`Found undefined/null value at ${currentPath}:`, value);
          } else if (typeof value === 'object' && value !== null) {
            checkForUndefined(value, currentPath);
          }
        }
      };

      checkForUndefined(completeInputData);

      // Submit inputs for each analysis
      const inputPromises = analysisIds.map(analysisId =>
        valuationAPI.submitInputs(analysisId, completeInputData)
      );

      await Promise.all(inputPromises);

      // Navigate to results with all analysis IDs
      const allIds = analysisIds.join(',');
      navigate(`/results/${allIds}`);
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error submitting form. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderArrayInput = (fieldName, label, required = false) => (
    <div>
      <label>{label} {required && '*'}</label>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
        {formData[fieldName].map((value, index) => (
          <input
            key={index}
            type="number"
            value={value}
            onChange={(e) => handleArrayInputChange(fieldName, index, e.target.value)}
            className="input"
            placeholder={`Year ${index + 1}`}
            step="0.1"
            required={required}
          />
        ))}
      </div>
    </div>
  );

  const renderMultiplesInput = (fieldName, label) => {
    // Handle nested field names like 'comparable_multiples.EV/EBITDA'
    const fieldParts = fieldName.split('.');
    let fieldData;
    if (fieldParts.length === 2) {
      fieldData = formData[fieldParts[0]]?.[fieldParts[1]];
    } else {
      fieldData = formData[fieldName];
    }

    if (!fieldData || !Array.isArray(fieldData)) {
      console.warn(`Field ${fieldName} not found or not an array:`, fieldData);
      return null;
    }

    return (
      <div>
        <label>{label}</label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
          {fieldData.map((value, index) => (
            <input
              key={index}
              type="number"
              value={value}
              onChange={(e) => {
                const newArray = [...fieldData];
                newArray[index] = parseFloat(e.target.value) || 0;

                if (fieldParts.length === 2) {
                  setFormData(prev => ({
                    ...prev,
                    [fieldParts[0]]: {
                      ...prev[fieldParts[0]],
                      [fieldParts[1]]: newArray
                    }
                  }));
                } else {
                  setFormData(prev => ({ ...prev, [fieldName]: newArray }));
                }
              }}
              className="input"
              placeholder={`Multiple ${index + 1}`}
              step="0.1"
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      <h1>Input Financial Data</h1>
      {/* CSV Upload Section */}
      <div className="card">
        <h2>Upload Inputs from CSV</h2>
        <CSVUpload onDataLoaded={handleCSVData} />
        <p className="text-sm text-gray-500 mt-2">You can download a sample CSV, fill it, and upload it here to auto-fill the form.</p>
      </div>

      <div className="card">
        <h2>Selected Analyses:</h2>
        <div style={{ marginBottom: '20px' }}>
          {selectedAnalyses.map(analysis => (
            <span key={analysis.id} className="selected-tag">
              {analysis.icon} {analysis.name}
            </span>
          ))}
        </div>
        <p>All selected analyses will use the same financial inputs below.</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Company Information */}
        <div className="card">
          <h2>Company Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <div>
              <label>Company Name *</label>
              <input
                type="text"
                name="company_name"
                value={formData.company_name}
                onChange={handleInputChange}
                className="input"
                required
              />
            </div>
            <div>
              <label>Valuation Date</label>
              <input
                type="date"
                name="valuation_date"
                value={formData.valuation_date}
                onChange={handleInputChange}
                className="input"
              />
            </div>
            <div>
              <label>Forecast Years</label>
              <input
                type="number"
                name="forecast_years"
                value={formData.forecast_years}
                onChange={handleInputChange}
                className="input"
                min="1"
                max="10"
              />
            </div>
          </div>
        </div>

        {/* Core Financial Inputs */}
        <div className="card">
          <h2>Core Financial Inputs</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <div>
              <label>EBIT Margin (%) *</label>
              <input
                type="number"
                name="ebit_margin"
                value={formData.ebit_margin}
                onChange={handleInputChange}
                className="input"
                step="0.01"
                min="0"
                max="1"
                required
              />
            </div>
            <div>
              <label>Tax Rate (%) *</label>
              <input
                type="number"
                name="tax_rate"
                value={formData.tax_rate}
                onChange={handleInputChange}
                className="input"
                step="0.01"
                min="0"
                max="1"
                required
              />
            </div>
            <div>
              <label>WACC (%) *</label>
              <input
                type="number"
                name="weighted_average_cost_of_capital"
                value={formData.weighted_average_cost_of_capital}
                onChange={handleInputChange}
                className="input"
                step="0.001"
                min="0"
                max="1"
                required
              />
            </div>
            <div>
              <label>Terminal Growth Rate (%) *</label>
              <input
                type="number"
                name="terminal_growth_rate"
                value={formData.terminal_growth_rate}
                onChange={handleInputChange}
                className="input"
                step="0.001"
                min="0"
                max="1"
                required
              />
            </div>
            <div>
              <label>Share Count (millions) *</label>
              <input
                type="number"
                name="share_count"
                value={formData.share_count}
                onChange={handleInputChange}
                className="input"
                step="0.1"
                required
              />
            </div>
            <div>
              <label>Cost of Debt (%) *</label>
              <input
                type="number"
                name="cost_of_debt"
                value={formData.cost_of_debt}
                onChange={handleInputChange}
                className="input"
                step="0.001"
                min="0"
                max="1"
                required
              />
            </div>
            <div>
              <label>Cash Balance (millions)</label>
              <input
                type="number"
                name="cash_balance"
                value={formData.cash_balance}
                onChange={handleInputChange}
                className="input"
                step="0.1"
              />
            </div>
          </div>
        </div>

        {/* Revenue Projections */}
        <div className="card">
          <h2>Revenue Projections (millions) *</h2>
          {renderArrayInput('revenue', 'Revenue', true)}
        </div>

        {/* Capital Expenditure */}
        <div className="card">
          <h2>Capital Expenditure (millions) *</h2>
          {renderArrayInput('capex', 'Capital Expenditure', true)}
        </div>

        {/* Depreciation */}
        <div className="card">
          <h2>Depreciation (millions) *</h2>
          {renderArrayInput('depreciation', 'Depreciation', true)}
        </div>

        {/* Net Working Capital Changes */}
        <div className="card">
          <h2>Net Working Capital Changes (millions) *</h2>
          {renderArrayInput('nwc_changes', 'NWC Changes', true)}
        </div>

        {/* Optional Items */}
        <div className="card">
          <h2>Optional Items (millions)</h2>
          {/* These fields are not directly mapped to formData.financial_inputs in the new structure,
              but they are part of the original formData. They are kept here for consistency
              with the original form's structure, but their values are not directly editable
              from the CSV upload or the new formData structure. */}
          {/* {renderArrayInput('amortization', 'Amortization')} */}
          {/* {renderArrayInput('other_non_cash', 'Other Non-Cash Items')} */}
          {/* {renderArrayInput('other_working_capital', 'Other Working Capital')} */}
        </div>

        {/* Cost of Capital - only if APV analysis is selected (needs unlevered cost of equity) */}
        {selectedAnalyses.some(analysis => analysis.id === 'apv') && (
          <div className="card">
            <h2>Cost of Capital</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <div>
                <label>Risk-Free Rate (%)</label>
                <input
                  type="number"
                  name="cost_of_capital.risk_free_rate"
                  value={formData.cost_of_capital.risk_free_rate}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                  min="0"
                  max="1"
                />
              </div>
              <div>
                <label>Market Risk Premium (%)</label>
                <input
                  type="number"
                  name="cost_of_capital.market_risk_premium"
                  value={formData.cost_of_capital.market_risk_premium}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                  min="0"
                  max="1"
                />
              </div>
              <div>
                <label>Levered Beta</label>
                <input
                  type="number"
                  name="cost_of_capital.levered_beta"
                  value={formData.cost_of_capital.levered_beta}
                  onChange={handleInputChange}
                  className="input"
                  step="0.1"
                />
              </div>
              <div>
                <label>Unlevered Beta</label>
                <input
                  type="number"
                  name="cost_of_capital.unlevered_beta"
                  value={formData.cost_of_capital.unlevered_beta}
                  onChange={handleInputChange}
                  className="input"
                  step="0.1"
                />
              </div>
              <div>
                <label>Target Debt-to-Value Ratio</label>
                <input
                  type="number"
                  name="cost_of_capital.target_debt_to_value_ratio"
                  value={formData.cost_of_capital.target_debt_to_value_ratio}
                  onChange={handleInputChange}
                  className="input"
                  step="0.01"
                  min="0"
                  max="1"
                />
              </div>
              <div className="grid">
                <div>
                  <label>Unlevered Cost of Equity</label>
                  <input
                    type="number"
                    name="cost_of_capital.unlevered_cost_of_equity"
                    value={formData.cost_of_capital.unlevered_cost_of_equity}
                    onChange={handleInputChange}
                    className="input"
                    step="0.01"
                    min="0"
                    max="1"
                  />
                </div>
                <div>
                  <label>Cost of Equity</label>
                  <input
                    type="number"
                    name="cost_of_capital.cost_of_equity"
                    value={formData.cost_of_capital.cost_of_equity}
                    onChange={handleInputChange}
                    className="input"
                    step="0.01"
                    min="0"
                    max="1"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Comparable Multiples - only if multiples analysis is selected */}
        {selectedAnalyses.some(analysis => analysis.id === 'multiples') && (
          <div className="card">
            <h2>Comparable Multiples</h2>
            {renderMultiplesInput('comparable_multiples.EV/EBITDA', 'EV/EBITDA Multiples')}
            {renderMultiplesInput('comparable_multiples.EV/Revenue', 'EV/Revenue Multiples')}
            {renderMultiplesInput('comparable_multiples.P/E', 'P/E Multiples')}
          </div>
        )}

        {/* Sensitivity Analysis - only if sensitivity analysis is selected */}
        {selectedAnalyses.some(analysis => analysis.id === 'sensitivity') && (
          <div className="card">
            <h2>Sensitivity Analysis Ranges</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <div>
                <label>WACC Range (min)</label>
                <input
                  type="number"
                  name="wacc_range_min"
                  value={formData.sensitivity_analysis.weighted_average_cost_of_capital[0]}
                  onChange={(e) => {
                    const newArray = [...formData.sensitivity_analysis.weighted_average_cost_of_capital];
                    newArray[0] = parseFloat(e.target.value) || 0;
                    setFormData(prev => ({ ...prev, sensitivity_analysis: { ...prev.sensitivity_analysis, weighted_average_cost_of_capital: newArray } }));
                  }}
                  className="input"
                  step="0.001"
                />
              </div>
              <div>
                <label>WACC Range (max)</label>
                <input
                  type="number"
                  name="wacc_range_max"
                  value={formData.sensitivity_analysis.weighted_average_cost_of_capital[4]}
                  onChange={(e) => {
                    const newArray = [...formData.sensitivity_analysis.weighted_average_cost_of_capital];
                    newArray[4] = parseFloat(e.target.value) || 0;
                    setFormData(prev => ({ ...prev, sensitivity_analysis: { ...prev.sensitivity_analysis, weighted_average_cost_of_capital: newArray } }));
                  }}
                  className="input"
                  step="0.001"
                />
              </div>
              <div>
                <label>EBIT Margin Range (min)</label>
                <input
                  type="number"
                  name="ebit_margin_range_min"
                  value={formData.sensitivity_analysis.ebit_margin[0]}
                  onChange={(e) => {
                    const newArray = [...formData.sensitivity_analysis.ebit_margin];
                    newArray[0] = parseFloat(e.target.value) || 0;
                    setFormData(prev => ({ ...prev, sensitivity_analysis: { ...prev.sensitivity_analysis, ebit_margin: newArray } }));
                  }}
                  className="input"
                  step="0.01"
                />
              </div>
              <div>
                <label>EBIT Margin Range (max)</label>
                <input
                  type="number"
                  name="ebit_margin_range_max"
                  value={formData.sensitivity_analysis.ebit_margin[4]}
                  onChange={(e) => {
                    const newArray = [...formData.sensitivity_analysis.ebit_margin];
                    newArray[4] = parseFloat(e.target.value) || 0;
                    setFormData(prev => ({ ...prev, sensitivity_analysis: { ...prev.sensitivity_analysis, ebit_margin: newArray } }));
                  }}
                  className="input"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        )}

        {/* Monte Carlo Parameters - only if monte_carlo analysis is selected */}
        {selectedAnalyses.some(analysis => analysis.id === 'monte_carlo') && (
          <div className="card">
            <h2>Monte Carlo Parameters</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <div>
                <label>EBIT Margin Mean</label>
                <input
                  type="number"
                  name="mc_ebit_margin_mean"
                  value={formData.monte_carlo_specs.ebit_margin.params.mean}
                  onChange={handleInputChange}
                  className="input"
                  step="0.01"
                />
              </div>
              <div>
                <label>EBIT Margin Std Dev</label>
                <input
                  type="number"
                  name="mc_ebit_margin_std"
                  value={formData.monte_carlo_specs.ebit_margin.params.std}
                  onChange={handleInputChange}
                  className="input"
                  step="0.01"
                />
              </div>
              <div>
                <label>WACC Mean</label>
                <input
                  type="number"
                  name="mc_wacc_mean"
                  value={formData.monte_carlo_specs.weighted_average_cost_of_capital.params.mean}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                />
              </div>
              <div>
                <label>WACC Std Dev</label>
                <input
                  type="number"
                  name="mc_wacc_std"
                  value={formData.monte_carlo_specs.weighted_average_cost_of_capital.params.std}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                />
              </div>
              <div>
                <label>Terminal Growth Mean</label>
                <input
                  type="number"
                  name="mc_terminal_growth_mean"
                  value={formData.monte_carlo_specs.terminal_growth_rate.params.mean}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                />
              </div>
              <div>
                <label>Terminal Growth Std Dev</label>
                <input
                  type="number"
                  name="mc_terminal_growth_std"
                  value={formData.monte_carlo_specs.terminal_growth_rate.params.std}
                  onChange={handleInputChange}
                  className="input"
                  step="0.001"
                />
              </div>
            </div>
          </div>
        )}

        <div className="card">
          <button
            type="submit"
            className="button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" style={{
                  display: 'inline-block',
                  width: '16px',
                  height: '16px',
                  border: '2px solid #ffffff',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  marginRight: '8px'
                }}></span>
                Processing...
              </>
            ) : (
              `Run ${selectedAnalyses.length} Analysis${selectedAnalyses.length > 1 ? 'es' : ''}`
            )}
          </button>
        </div>
      </form>

      {/* Loading Overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div className="card" style={{ textAlign: 'center', padding: '40px', maxWidth: '400px' }}>
            <div className="spinner" style={{
              width: '50px',
              height: '50px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #3498db',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 20px'
            }}></div>
            <h2>Processing Your Analysis</h2>
            <p>Please wait while we process your financial inputs and run the valuation calculations.</p>
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        </div>
      )}
    </div>
  );
}

export default InputForm; 