import {
  Box,
  Button,
  Paper,
  Step,
  StepLabel,
  Stepper,
  Typography
} from '@mui/material';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AdvancedAnalysis from './form/AdvancedAnalysis';
import AnalysisSelection from './form/AnalysisSelection';
import FinancialProjections from './form/FinancialProjections';
import ValuationAssumptions from './form/ValuationAssumptions';
import LoadingSpinner from './LoadingSpinner';

const steps = [
  'Select Analyses',
  'Financial Projections',
  'Valuation Assumptions',
  'Advanced Analysis'
];

const ValuationForm = ({ setResults, setLoading, loading }) => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    analyses: ['WACC DCF', 'APV DCF'],
    financialProjections: {
      inputMode: 'driver',
      revenue: [50000000, 55000000, 60000000, 65000000, 70000000],
      ebitMargin: 0.15,
      capex: [5000000, 5500000, 6000000, 6500000, 7000000],
      depreciation: [4000000, 4400000, 4800000, 5200000, 5600000],
      nwcChanges: [1000000, 1100000, 1200000, 1300000, 1400000],
      fcfSeries: [],
      shareCount: 10000000,
      costOfDebt: 0.06,
      debtSchedule: {},
    },
    valuationAssumptions: {
      terminalGrowth: 0.025,
      wacc: 0.12,
      taxRate: 0.25,
      midYearConvention: false,
    },
    advancedAnalysis: {
      mcRuns: 1000,
      variableSpecs: {
        wacc: {
          dist: 'normal',
          params: { loc: 0.12, scale: 0.01 }  // Reduced std dev from 0.02 to 0.01
        },
        terminal_growth: {
          dist: 'uniform',  // Changed from 'normal' to 'uniform'
          params: { low: 0.015, high: 0.025 }  // Reduced max from 0.035 to 0.025
        }
      },
      scenarios: {},
      sensitivityRanges: {},
      compsData: null,
    },
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  // Validation function
  const validateFormData = (data) => {
    const errors = [];

    if (!data.analyses || data.analyses.length === 0) {
      errors.push("Please select at least one analysis type");
    }

    if (data.financialProjections.inputMode === 'driver') {
      if (!data.financialProjections.revenue || data.financialProjections.revenue.length === 0) {
        errors.push("Revenue series is required");
      }
      if (!data.financialProjections.capex || data.financialProjections.capex.length === 0) {
        errors.push("CapEx series is required");
      }
      if (!data.financialProjections.depreciation || data.financialProjections.depreciation.length === 0) {
        errors.push("Depreciation series is required");
      }
      if (!data.financialProjections.nwcChanges || data.financialProjections.nwcChanges.length === 0) {
        errors.push("NWC changes series is required");
      }

      // Check series lengths match
      const series = [
        data.financialProjections.revenue,
        data.financialProjections.capex,
        data.financialProjections.depreciation,
        data.financialProjections.nwcChanges
      ].filter(s => s && s.length > 0);

      if (series.length > 1) {
        const lengths = series.map(s => s.length);
        if (new Set(lengths).size > 1) {
          errors.push("All financial series must have the same length");
        }
      }
    } else {
      if (!data.financialProjections.fcfSeries || data.financialProjections.fcfSeries.length === 0) {
        errors.push("FCF series is required");
      }
    }

    return errors;
  };

  const handleSubmit = async () => {
    // Create a copy of formData for processing
    let processedData = { ...formData };

    // Auto-clean analyses: remove Sensitivity if no ranges configured
    if (processedData.analyses.includes('Sensitivity')) {
      const hasSensitivityRanges = Object.keys(processedData.advancedAnalysis.sensitivityRanges || {}).length > 0;
      if (!hasSensitivityRanges) {
        processedData.analyses = processedData.analyses.filter(a => a !== 'Sensitivity');
        console.log('Auto-removed Sensitivity analysis - no parameters configured');
        console.log('Original analyses:', formData.analyses);
        console.log('Cleaned analyses:', processedData.analyses);
      }
    }

    // Validate form data
    const validationErrors = validateFormData(processedData);
    if (validationErrors.length > 0) {
      alert('Validation errors:\n' + validationErrors.join('\n'));
      return;
    }

    setLoading(true);
    try {
      // Fixed convertSensitivityRanges function - remove the division by 100
      const convertSensitivityRanges = (ranges) => {
        console.log('Converting sensitivity ranges:', ranges);
        const converted = {};
        for (const [param, config] of Object.entries(ranges)) {
          console.log('Processing param:', param, 'config:', config);
          if (config && typeof config === 'object' && 'min' in config && 'max' in config && 'steps' in config) {
            const { min, max, steps } = config;
            const values = [];
            for (let i = 0; i < steps; i++) {
              const value = min + (max - min) * (i / (steps - 1));
              // Don't divide by 100 - send as decimal values
              values.push(value);
            }
            converted[param] = values;
            console.log('Converted values for', param, ':', values);
          } else {
            console.log('Invalid config for', param, ':', config);
          }
        }
        console.log('Final converted ranges:', converted);
        return converted;
      };

      // Transform data to match backend API expectations (camelCase to snake_case)
      const requestData = {
        // Analysis types (use processed analyses)
        analyses: processedData.analyses,

        // Financial projections (map camelCase to snake_case)
        revenue: processedData.financialProjections.revenue,
        ebit_margin: processedData.financialProjections.ebitMargin,
        capex: processedData.financialProjections.capex,
        depreciation: processedData.financialProjections.depreciation,
        nwc_changes: processedData.financialProjections.nwcChanges,
        fcf_series: processedData.financialProjections.fcfSeries,

        // Valuation assumptions (map camelCase to snake_case)
        terminal_growth: processedData.valuationAssumptions.terminalGrowth,
        wacc: processedData.valuationAssumptions.wacc,
        tax_rate: processedData.valuationAssumptions.taxRate,
        mid_year_convention: processedData.valuationAssumptions.midYearConvention,
        share_count: processedData.financialProjections.shareCount,
        cost_of_debt: processedData.financialProjections.costOfDebt,
        debt_schedule: processedData.financialProjections.debtSchedule,

        // Advanced analysis
        mc_runs: processedData.advancedAnalysis.mcRuns,
        variable_specs: processedData.advancedAnalysis.variableSpecs,
        scenarios: processedData.advancedAnalysis.scenarios,
        sensitivity_ranges: convertSensitivityRanges(processedData.advancedAnalysis.sensitivityRanges),
        comps_data: processedData.advancedAnalysis.compsData,
      };

      console.log('Sending request data:', requestData);
      console.log('Analyses being sent:', requestData.analyses);
      console.log('Sensitivity ranges being sent:', requestData.sensitivity_ranges);
      console.log('Raw sensitivity ranges from form:', processedData.advancedAnalysis.sensitivityRanges);
      console.log('Comps data being sent:', processedData.advancedAnalysis.compsData);
      console.log('Variable specs being sent:', requestData.variable_specs);

      // Use environment variable for backend URL in production
      const apiBase = process.env.REACT_APP_API_URL || '';
      console.log('API base:', apiBase);
      const response = await fetch(`${apiBase}/api/valuation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          console.log('Could not parse error response as JSON');
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Received result:', result);

      // Extract the results from the response structure
      if (result.success && result.results) {
        setResults(result.results);
        navigate('/results');
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Error running valuation:', error);
      console.error('Error running valuation message: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (section, data) => {
    setFormData(prev => ({
      ...prev,
      [section]: { ...prev[section], ...data }
    }));
  };

  return (
    <Box className="fade-in">
      <Paper
        sx={{
          p: { xs: 2, md: 4 },
          maxWidth: 1200,
          mx: 'auto',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}
        className="card-hover"
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h3"
            gutterBottom
            className="gradient-text"
            sx={{ fontWeight: 700, mb: 1 }}
          >
            Financial Valuation Tool
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ maxWidth: 600, mx: 'auto' }}
          >
            Advanced DCF analysis with Monte Carlo simulations, sensitivity analysis, and scenario modeling
          </Typography>
        </Box>

        <Stepper
          activeStep={activeStep}
          sx={{
            mb: 4,
            '& .MuiStepLabel-root .Mui-completed': {
              color: 'secondary.main',
            },
            '& .MuiStepLabel-root .Mui-active': {
              color: 'primary.main',
            },
          }}
        >
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ minHeight: 400 }}>
          {loading ? (
            <LoadingSpinner message="Running comprehensive valuation analysis..." />
          ) : (
            <>
              {activeStep === 0 && (
                <AnalysisSelection
                  analyses={formData.analyses}
                  onUpdate={(analyses) => setFormData(prev => ({ ...prev, analyses }))}
                />
              )}

              {activeStep === 1 && (
                <FinancialProjections
                  data={formData.financialProjections}
                  onUpdate={(data) => updateFormData('financialProjections', data)}
                />
              )}

              {activeStep === 2 && (
                <ValuationAssumptions
                  data={formData.valuationAssumptions}
                  onUpdate={(data) => updateFormData('valuationAssumptions', data)}
                />
              )}

              {activeStep === 3 && (
                <AdvancedAnalysis
                  data={formData.advancedAnalysis}
                  analyses={formData.analyses}
                  onUpdate={(data) => updateFormData('advancedAnalysis', data)}
                />
              )}
            </>
          )}
        </Box>

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            mt: 4,
            pt: 3,
            borderTop: '1px solid',
            borderColor: 'grey.200',
          }}
        >
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            variant="outlined"
            sx={{
              minWidth: 120,
              borderRadius: 2,
            }}
          >
            Back
          </Button>

          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              sx={{
                minWidth: 160,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                },
              }}
            >
              Run Valuation
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
              sx={{
                minWidth: 120,
                borderRadius: 2,
              }}
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default ValuationForm; 