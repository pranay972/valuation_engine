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

    // Core Financial Inputs
    revenue: [1000, 1100, 1200, 1300, 1400],
    ebit_margin: 0.18,
    tax_rate: 0.25,
    capex: [150, 165, 180, 195, 210],
    depreciation: [100, 110, 120, 130, 140],
    nwc_changes: [50, 55, 60, 65, 70],
    amortization: [25, 27.5, 30, 32.5, 35],
    other_non_cash: [10, 11, 12, 13, 14],
    other_working_capital: [5, 5.5, 6, 6.5, 7],
    weighted_average_cost_of_capital: 0.095,
    terminal_growth_rate: 0.025,
    share_count: 45.2,
    cost_of_debt: 0.065,
    cash_balance: 50.0,

    // Cost of Capital
    risk_free_rate: 0.03,
    market_risk_premium: 0.06,
    levered_beta: 1.2,
    unlevered_beta: 1.0,
    target_debt_to_value_ratio: 0.3,
    unlevered_cost_of_equity: 0.11,

    // Debt Schedule
    debt_schedule: {
      "0": 150.0,
      "1": 135.0,
      "2": 120.0,
      "3": 105.0,
      "4": 90.0
    },

    // Comparable Multiples
    ev_ebitda: [12.5, 14.2, 13.8, 15.1, 12.9, 13.5, 14.8, 13.2],
    pe_ratio: [18.5, 22.1, 20.8, 24.3, 19.7, 21.5, 23.2, 20.1],
    ev_fcf: [15.2, 17.8, 16.5, 18.9, 15.8, 17.2, 18.5, 16.1],
    ev_revenue: [2.8, 3.2, 3.0, 3.5, 2.9, 3.1, 3.4, 3.0],

    // Sensitivity Analysis
    wacc_range: [0.075, 0.085, 0.095, 0.105, 0.115],
    ebit_margin_range: [0.14, 0.16, 0.18, 0.20, 0.22],
    terminal_growth_range: [0.015, 0.020, 0.025, 0.030, 0.035],
    target_debt_ratio_range: [0.1, 0.2, 0.3, 0.4, 0.5],

    // Monte Carlo Specs
    mc_ebit_margin_mean: 0.18,
    mc_ebit_margin_std: 0.02,
    mc_wacc_mean: 0.095,
    mc_wacc_std: 0.01,
    mc_terminal_growth_mean: 0.025,
    mc_terminal_growth_std: 0.005,
    mc_levered_beta_mean: 1.2,
    mc_levered_beta_std: 0.1
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
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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

      // Prepare the complete input data
      const completeInputData = {
        company_name: formData.company_name,
        valuation_date: formData.valuation_date,
        forecast_years: parseInt(formData.forecast_years),
        financial_inputs: {
          revenue: formData.revenue,
          ebit_margin: parseFloat(formData.ebit_margin),
          tax_rate: parseFloat(formData.tax_rate),
          capex: formData.capex,
          depreciation: formData.depreciation,
          nwc_changes: formData.nwc_changes,
          amortization: formData.amortization,
          other_non_cash: formData.other_non_cash,
          other_working_capital: formData.other_working_capital,
          weighted_average_cost_of_capital: parseFloat(formData.weighted_average_cost_of_capital),
          terminal_growth_rate: parseFloat(formData.terminal_growth_rate),
          share_count: parseFloat(formData.share_count),
          cost_of_debt: parseFloat(formData.cost_of_debt),
          cash_balance: parseFloat(formData.cash_balance),
          // APV-specific fields (required for APV analysis)
          unlevered_cost_of_equity: parseFloat(formData.unlevered_cost_of_equity),
          // Additional cost of capital fields
          risk_free_rate: parseFloat(formData.risk_free_rate),
          market_risk_premium: parseFloat(formData.market_risk_premium),
          levered_beta: parseFloat(formData.levered_beta),
          unlevered_beta: parseFloat(formData.unlevered_beta),
          target_debt_to_value_ratio: parseFloat(formData.target_debt_to_value_ratio),
          debt_schedule: formData.debt_schedule
        },
        comparable_multiples: {
          "EV/EBITDA": formData.ev_ebitda,
          "P/E": formData.pe_ratio,
          "EV/FCF": formData.ev_fcf,
          "EV/Revenue": formData.ev_revenue
        },
        sensitivity_analysis: {
          wacc_range: formData.wacc_range,
          ebit_margin_range: formData.ebit_margin_range,
          terminal_growth_range: formData.terminal_growth_range,
          target_debt_ratio_range: formData.target_debt_ratio_range
        },
        monte_carlo_specs: {
          ebit_margin: {
            distribution: "normal",
            params: {
              mean: parseFloat(formData.mc_ebit_margin_mean),
              std: parseFloat(formData.mc_ebit_margin_std)
            }
          },
          weighted_average_cost_of_capital: {
            distribution: "normal",
            params: {
              mean: parseFloat(formData.mc_wacc_mean),
              std: parseFloat(formData.mc_wacc_std)
            }
          },
          terminal_growth_rate: {
            distribution: "normal",
            params: {
              mean: parseFloat(formData.mc_terminal_growth_mean),
              std: parseFloat(formData.mc_terminal_growth_std)
            }
          },
          levered_beta: {
            distribution: "normal",
            params: {
              mean: parseFloat(formData.mc_levered_beta_mean),
              std: parseFloat(formData.mc_levered_beta_std)
            }
          }
        }
      };

      // Submit inputs for each analysis
      const inputPromises = analysisIds.map(analysisId =>
        valuationAPI.submitInputs(analysisId, {
          financial_inputs: completeInputData.financial_inputs,
          comparable_multiples: completeInputData.comparable_multiples,
          scenarios: completeInputData.scenarios,
          sensitivity_analysis: completeInputData.sensitivity_analysis,
          monte_carlo_specs: completeInputData.monte_carlo_specs
        })
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

  const renderMultiplesInput = (fieldName, label) => (
    <div>
      <label>{label}</label>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        {formData[fieldName].map((value, index) => (
          <input
            key={index}
            type="number"
            value={value}
            onChange={(e) => {
              const newArray = [...formData[fieldName]];
              newArray[index] = parseFloat(e.target.value) || 0;
              setFormData(prev => ({ ...prev, [fieldName]: newArray }));
            }}
            className="input"
            placeholder={`Multiple ${index + 1}`}
            step="0.1"
          />
        ))}
      </div>
    </div>
  );

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
          {renderArrayInput('amortization', 'Amortization')}
          {renderArrayInput('other_non_cash', 'Other Non-Cash Items')}
          {renderArrayInput('other_working_capital', 'Other Working Capital')}
        </div>

        {/* Cost of Capital */}
        <div className="card">
          <h2>Cost of Capital</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <label>Risk-Free Rate (%)</label>
              <input
                type="number"
                name="risk_free_rate"
                value={formData.risk_free_rate}
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
                name="market_risk_premium"
                value={formData.market_risk_premium}
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
                name="levered_beta"
                value={formData.levered_beta}
                onChange={handleInputChange}
                className="input"
                step="0.1"
              />
            </div>
            <div>
              <label>Unlevered Beta</label>
              <input
                type="number"
                name="unlevered_beta"
                value={formData.unlevered_beta}
                onChange={handleInputChange}
                className="input"
                step="0.1"
              />
            </div>
            <div>
              <label>Target Debt-to-Value Ratio</label>
              <input
                type="number"
                name="target_debt_to_value_ratio"
                value={formData.target_debt_to_value_ratio}
                onChange={handleInputChange}
                className="input"
                step="0.01"
                min="0"
                max="1"
              />
            </div>
            <div>
              <label>Unlevered Cost of Equity (%)</label>
              <input
                type="number"
                name="unlevered_cost_of_equity"
                value={formData.unlevered_cost_of_equity}
                onChange={handleInputChange}
                className="input"
                step="0.001"
                min="0"
                max="1"
              />
            </div>
          </div>
        </div>

        {/* Comparable Multiples */}
        <div className="card">
          <h2>Comparable Multiples</h2>
          {renderMultiplesInput('ev_ebitda', 'EV/EBITDA Multiples')}
          {renderMultiplesInput('pe_ratio', 'P/E Multiples')}
          {renderMultiplesInput('ev_fcf', 'EV/FCF Multiples')}
          {renderMultiplesInput('ev_revenue', 'EV/Revenue Multiples')}
        </div>

        {/* Sensitivity Analysis */}
        <div className="card">
          <h2>Sensitivity Analysis Ranges</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <label>WACC Range (min)</label>
              <input
                type="number"
                name="wacc_range_min"
                value={formData.wacc_range[0]}
                onChange={(e) => {
                  const newArray = [...formData.wacc_range];
                  newArray[0] = parseFloat(e.target.value) || 0;
                  setFormData(prev => ({ ...prev, wacc_range: newArray }));
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
                value={formData.wacc_range[4]}
                onChange={(e) => {
                  const newArray = [...formData.wacc_range];
                  newArray[4] = parseFloat(e.target.value) || 0;
                  setFormData(prev => ({ ...prev, wacc_range: newArray }));
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
                value={formData.ebit_margin_range[0]}
                onChange={(e) => {
                  const newArray = [...formData.ebit_margin_range];
                  newArray[0] = parseFloat(e.target.value) || 0;
                  setFormData(prev => ({ ...prev, ebit_margin_range: newArray }));
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
                value={formData.ebit_margin_range[4]}
                onChange={(e) => {
                  const newArray = [...formData.ebit_margin_range];
                  newArray[4] = parseFloat(e.target.value) || 0;
                  setFormData(prev => ({ ...prev, ebit_margin_range: newArray }));
                }}
                className="input"
                step="0.01"
              />
            </div>
          </div>
        </div>

        {/* Monte Carlo Parameters */}
        <div className="card">
          <h2>Monte Carlo Parameters</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <label>EBIT Margin Mean</label>
              <input
                type="number"
                name="mc_ebit_margin_mean"
                value={formData.mc_ebit_margin_mean}
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
                value={formData.mc_ebit_margin_std}
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
                value={formData.mc_wacc_mean}
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
                value={formData.mc_wacc_std}
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
                value={formData.mc_terminal_growth_mean}
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
                value={formData.mc_terminal_growth_std}
                onChange={handleInputChange}
                className="input"
                step="0.001"
              />
            </div>
          </div>
        </div>

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