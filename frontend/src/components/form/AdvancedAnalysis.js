import React, { useState } from 'react';
import {
  Typography,
  Grid,
  TextField,
  FormControlLabel,
  Box,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  Button,
  Alert,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ClearIcon from '@mui/icons-material/Clear';

const AdvancedAnalysis = ({ data, analyses, onUpdate }) => {
  const [compsFile, setCompsFile] = useState(null);
  const [errors, setErrors] = useState({});

  // Initialize Monte Carlo with defaults if selected but not configured
  React.useEffect(() => {
    if (analyses.includes('Monte Carlo') && (!data.mcRuns || !data.variableSpecs || Object.keys(data.variableSpecs).length === 0)) {
      const defaultConfig = {
        mcRuns: 2000,
        variableSpecs: {
          wacc: {
            dist: 'normal',
            params: { loc: 0.12, scale: 0.01 }
          },
          terminal_growth: {
            dist: 'uniform',
            params: { low: 0.015, high: 0.025 }
          }
        }
      };
      onUpdate(defaultConfig);
    }
  }, [analyses, data.mcRuns, data.variableSpecs, onUpdate]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setCompsFile(file);
      
      // Read the file and store the data
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csv = e.target.result;
          const lines = csv.split('\n');
          const headers = lines[0].split(',').map(h => h.trim());
          const data = [];
          
          for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
              const values = lines[i].split(',');
              const row = {};
              headers.forEach((header, index) => {
                const value = values[index] ? values[index].trim() : '';
                // Convert numeric values to numbers, keep strings as strings
                if (header.includes('/') || !isNaN(value)) {
                  row[header] = isNaN(value) ? value : parseFloat(value);
                } else {
                  row[header] = value;
                }
              });
              data.push(row);
            }
          }
          
          console.log('Parsed comps data:', data);
          console.log('Number of rows:', data.length);
          console.log('Sample row:', data[0]);
          onUpdate({ compsData: data });
        } catch (error) {
          console.error('Error parsing CSV file:', error);
          alert('Error parsing CSV file. Please check the file format.');
        }
      };
      reader.onerror = () => {
        console.error('Error reading file');
        alert('Error reading file. Please try again.');
      };
      reader.readAsText(file);
    } else {
      alert('Please select a valid CSV file.');
    }
  };

  const handleMonteCarloChange = (field, value) => {
    setErrors(prev => ({ ...prev, [field]: null }));
    
    if (field === 'mcRuns') {
      const numValue = parseInt(value);
      if (isNaN(numValue) || numValue < 100 || numValue > 10000) {
        setErrors(prev => ({ ...prev, [field]: 'Number of runs must be between 100 and 10,000' }));
        return;
      }
    }
    
    // Ensure we have default variable specs if none exist
    let newData = {
      mcRuns: field === 'mcRuns' ? value : (data.mcRuns || 2000),
      variableSpecs: field === 'variableSpecs' ? value : (data.variableSpecs || {})
    };
    
    // If no variable specs exist, create default ones
    if (!newData.variableSpecs || Object.keys(newData.variableSpecs).length === 0) {
      newData.variableSpecs = {
        wacc: {
          dist: 'normal',
          params: { loc: 0.12, scale: 0.01 }
        },
        terminal_growth: {
          dist: 'uniform',
          params: { low: 0.015, high: 0.025 }
        }
      };
    }
    
    onUpdate(newData);
  };

  const handleMonteCarloVariableChange = (variableName, field, value) => {
    setErrors(prev => ({ ...prev, [`${variableName}_${field}`]: null }));
    
    const currentSpecs = data.variableSpecs || {};
    const currentVar = currentSpecs[variableName] || {};
    
    // Ensure we have a complete variable specification
    const newVar = {
      ...currentVar,
      [field]: value
    };
    
    // Set default values if not present
    if (field === 'dist' && !newVar.params) {
      if (value === 'normal') {
        newVar.params = variableName === 'wacc' ? { loc: 0.12, scale: 0.01 } :
                       variableName === 'terminal_growth' ? { loc: 0.02, scale: 0.005 } :
                       { loc: 0.15, scale: 0.02 };
      } else if (value === 'uniform') {
        newVar.params = variableName === 'wacc' ? { low: 0.10, high: 0.14 } :
                       variableName === 'terminal_growth' ? { low: 0.015, high: 0.025 } :
                       { low: 0.10, high: 0.20 };
      }
    }
    
    // Validate parameter values
    if (field === 'params' && newVar.params) {
      if (newVar.dist === 'normal') {
        if (newVar.params.scale <= 0) {
          setErrors(prev => ({ ...prev, [`${variableName}_scale`]: 'Standard deviation must be positive' }));
          return;
        }
      } else if (newVar.dist === 'uniform') {
        if (newVar.params.low >= newVar.params.high) {
          setErrors(prev => ({ ...prev, [`${variableName}_range`]: 'Minimum must be less than maximum' }));
          return;
        }
      }
    }
    
    const newSpecs = {
      ...currentSpecs,
      [variableName]: newVar
    };
    
    onUpdate({ variableSpecs: newSpecs });
  };

  const handleScenarioChange = (scenarioName, field, value) => {
    const newScenarios = { ...data.scenarios };
    if (!newScenarios[scenarioName]) {
      newScenarios[scenarioName] = {};
    }
    newScenarios[scenarioName][field] = value;
    onUpdate({ scenarios: newScenarios });
  };

  const handleSensitivityChange = (param, field, value) => {
    setErrors(prev => ({ ...prev, [`${param}_${field}`]: null }));
    
    const currentRanges = data.sensitivityRanges || {};
    const currentParam = currentRanges[param] || {};
    
    // Validate input
    if (field === 'min' || field === 'max') {
      const numValue = parseFloat(value);
      if (isNaN(numValue)) {
        setErrors(prev => ({ ...prev, [`${param}_${field}`]: 'Please enter a valid number' }));
        return;
      }
      
      if (field === 'min' && currentParam.max && numValue >= currentParam.max) {
        setErrors(prev => ({ ...prev, [`${param}_${field}`]: 'Minimum must be less than maximum' }));
        return;
      }
      
      if (field === 'max' && currentParam.min && numValue <= currentParam.min) {
        setErrors(prev => ({ ...prev, [`${param}_${field}`]: 'Maximum must be greater than minimum' }));
        return;
      }
    }
    
    if (field === 'steps') {
      const numValue = parseInt(value);
      if (isNaN(numValue) || numValue < 2 || numValue > 20) {
        setErrors(prev => ({ ...prev, [`${param}_${field}`]: 'Steps must be between 2 and 20' }));
        return;
      }
    }
    
    const newSensitivity = {
      ...currentRanges,
      [param]: {
        ...currentParam,
        [field]: value
      }
    };
    
    onUpdate({ sensitivityRanges: newSensitivity });
  };

  const handleSensitivityCheckbox = (param, checked, defaultConfig) => {
    if (checked) {
      const currentRanges = data.sensitivityRanges || {};
      const newSensitivity = {
        ...currentRanges,
        [param]: {
          min: defaultConfig.min / 100,  // Convert percentage to decimal (5% -> 0.05)
          max: defaultConfig.max / 100,  // Convert percentage to decimal (15% -> 0.15)
          steps: 5
        }
      };
      console.log('Setting sensitivity range for', param, ':', newSensitivity[param]);
      onUpdate({ sensitivityRanges: newSensitivity });
    } else {
      const currentRanges = data.sensitivityRanges || {};
      const newSensitivity = { ...currentRanges };
      delete newSensitivity[param];
      console.log('Removing sensitivity range for', param);
      onUpdate({ sensitivityRanges: newSensitivity });
    }
  };

  const clearField = (field) => {
    onUpdate({ [field]: field === 'mcRuns' ? 1000 : {} });
    setErrors(prev => ({ ...prev, [field]: null }));
  };

  const clearVariableField = (variableName, field) => {
    const currentSpecs = data.variableSpecs || {};
    const currentVar = currentSpecs[variableName] || {};
    const newVar = { ...currentVar };
    delete newVar[field];
    
    const newSpecs = {
      ...currentSpecs,
      [variableName]: newVar
    };
    
    onUpdate({ variableSpecs: newSpecs });
    setErrors(prev => ({ ...prev, [`${variableName}_${field}`]: null }));
  };

  if (!analyses.some(a => ['Monte Carlo', 'Multiples', 'Scenarios', 'Sensitivity'].includes(a))) {
    return (
      <div>
        <Typography variant="h5" gutterBottom>
          Advanced Analysis
        </Typography>
        <Alert severity="info">
          Select advanced analyses from the first step to configure their parameters here.
        </Alert>
        <Typography variant="body1" sx={{ mt: 2 }}>
          <strong>Available Advanced Analyses:</strong>
        </Typography>
        <ul>
          <li><strong>Monte Carlo Simulation:</strong> Uncertainty analysis with probability distributions</li>
          <li><strong>Comparable Multiples:</strong> Peer company analysis using industry ratios</li>
          <li><strong>Scenario Analysis:</strong> "What-if" testing with parameter overrides</li>
          <li><strong>Sensitivity Analysis:</strong> Parameter impact assessment</li>
        </ul>
      </div>
    );
  }

  return (
    <div>
      <Typography variant="h5" gutterBottom>
        Advanced Analysis Parameters
      </Typography>
      
      <Grid container spacing={3}>
        {analyses.includes('Monte Carlo') && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monte Carlo Analysis
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Monte Carlo Simulation Overview:
                  </Typography>
                  <Typography variant="body2">
                    Monte Carlo simulation uses probability distributions to model uncertainty in key parameters.
                    This helps understand the range of possible valuation outcomes and their likelihood.
                  </Typography>
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Number of Runs"
                      type="number"
                      value={data.mcRuns || 2000}
                      onChange={(e) => handleMonteCarloChange('mcRuns', parseInt(e.target.value))}
                      inputProps={{ min: 100, max: 10000 }}
                      helperText={errors.mcRuns || "Number of Monte Carlo simulations (100-10,000)"}
                      error={!!errors.mcRuns}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <Tooltip title="Reset to default">
                              <IconButton
                                size="small"
                                onClick={() => clearField('mcRuns')}
                                edge="end"
                              >
                                <ClearIcon />
                              </IconButton>
                            </Tooltip>
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>

                <Typography variant="subtitle1" sx={{ mt: 3, mb: 2 }}>
                  Variable Specifications
                </Typography>
                
                {[
                  { key: 'wacc', label: 'WACC', description: 'Weighted Average Cost of Capital' },
                  { key: 'ebit_margin', label: 'EBIT Margin', description: 'Operating profit margin' },
                  { key: 'terminal_growth', label: 'Terminal Growth', description: 'Long-term growth rate' }
                ].map((variable) => (
                  <Accordion key={variable.key} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={!!data.variableSpecs?.[variable.key]}
                            onChange={(e) => {
                              if (e.target.checked) {
                                // Initialize with complete specification
                                const newSpecs = {
                                  ...data.variableSpecs,
                                  [variable.key]: variable.key === 'terminal_growth' ? {
                                    dist: 'uniform',
                                    params: { low: 0.015, high: 0.025 }
                                  } : {
                                    dist: 'normal',
                                    params: variable.key === 'wacc' ? { loc: 0.12, scale: 0.01 } : 
                                           { loc: 0.15, scale: 0.02 }
                                  }
                                };
                                onUpdate({ variableSpecs: newSpecs });
                              } else {
                                const currentSpecs = data.variableSpecs || {};
                                const newSpecs = { ...currentSpecs };
                                delete newSpecs[variable.key];
                                onUpdate({ variableSpecs: newSpecs });
                              }
                            }}
                          />
                        }
                        label={`Model ${variable.label} uncertainty`}
                      />
                    </AccordionSummary>
                    {data.variableSpecs?.[variable.key] && (
                      <AccordionDetails>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {variable.description}
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <FormControl component="fieldset">
                              <FormLabel component="legend">Distribution Type</FormLabel>
                              <RadioGroup
                                value={data.variableSpecs[variable.key].dist || 'normal'}
                                onChange={(e) => handleMonteCarloVariableChange(variable.key, 'dist', e.target.value)}
                              >
                                <FormControlLabel value="normal" control={<Radio />} label="Normal Distribution" />
                                <FormControlLabel value="uniform" control={<Radio />} label="Uniform Distribution" />
                              </RadioGroup>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            {data.variableSpecs[variable.key].dist === 'normal' ? (
                              <>
                                <TextField
                                  fullWidth
                                  label="Mean"
                                  type="number"
                                  value={data.variableSpecs[variable.key].params?.loc || 0.1}
                                  onChange={(e) => handleMonteCarloVariableChange(variable.key, 'params', {
                                    ...data.variableSpecs[variable.key].params,
                                    loc: parseFloat(e.target.value)
                                  })}
                                  helperText={errors[`${variable.key}_loc`] || "Mean value for normal distribution"}
                                  error={!!errors[`${variable.key}_loc`]}
                                  sx={{ mb: 1 }}
                                  InputProps={{
                                    endAdornment: (
                                      <InputAdornment position="end">
                                        <Tooltip title="Reset to default">
                                          <IconButton
                                            size="small"
                                            onClick={() => clearVariableField(variable.key, 'params')}
                                            edge="end"
                                          >
                                            <ClearIcon />
                                          </IconButton>
                                        </Tooltip>
                                      </InputAdornment>
                                    ),
                                  }}
                                />
                                <TextField
                                  fullWidth
                                  label="Standard Deviation"
                                  type="number"
                                  value={data.variableSpecs[variable.key].params?.scale || 0.02}
                                  onChange={(e) => handleMonteCarloVariableChange(variable.key, 'params', {
                                    ...data.variableSpecs[variable.key].params,
                                    scale: parseFloat(e.target.value)
                                  })}
                                  helperText={errors[`${variable.key}_scale`] || "Standard deviation (must be positive)"}
                                  error={!!errors[`${variable.key}_scale`]}
                                  InputProps={{
                                    endAdornment: (
                                      <InputAdornment position="end">
                                        <Tooltip title="Reset to default">
                                          <IconButton
                                            size="small"
                                            onClick={() => clearVariableField(variable.key, 'params')}
                                            edge="end"
                                          >
                                            <ClearIcon />
                                          </IconButton>
                                        </Tooltip>
                                      </InputAdornment>
                                    ),
                                  }}
                                />
                              </>
                            ) : (
                              <>
                                <TextField
                                  fullWidth
                                  label="Minimum"
                                  type="number"
                                  value={data.variableSpecs[variable.key].params?.low || 0.05}
                                  onChange={(e) => handleMonteCarloVariableChange(variable.key, 'params', {
                                    ...data.variableSpecs[variable.key].params,
                                    low: parseFloat(e.target.value)
                                  })}
                                  helperText={errors[`${variable.key}_range`] || "Minimum value for uniform distribution"}
                                  error={!!errors[`${variable.key}_range`]}
                                  sx={{ mb: 1 }}
                                  InputProps={{
                                    endAdornment: (
                                      <InputAdornment position="end">
                                        <Tooltip title="Reset to default">
                                          <IconButton
                                            size="small"
                                            onClick={() => clearVariableField(variable.key, 'params')}
                                            edge="end"
                                          >
                                            <ClearIcon />
                                          </IconButton>
                                        </Tooltip>
                                      </InputAdornment>
                                    ),
                                  }}
                                />
                                <TextField
                                  fullWidth
                                  label="Maximum"
                                  type="number"
                                  value={data.variableSpecs[variable.key].params?.high || 0.15}
                                  onChange={(e) => handleMonteCarloVariableChange(variable.key, 'params', {
                                    ...data.variableSpecs[variable.key].params,
                                    high: parseFloat(e.target.value)
                                  })}
                                  helperText={errors[`${variable.key}_range`] || "Maximum value for uniform distribution"}
                                  error={!!errors[`${variable.key}_range`]}
                                  InputProps={{
                                    endAdornment: (
                                      <InputAdornment position="end">
                                        <Tooltip title="Reset to default">
                                          <IconButton
                                            size="small"
                                            onClick={() => clearVariableField(variable.key, 'params')}
                                            edge="end"
                                          >
                                            <ClearIcon />
                                          </IconButton>
                                        </Tooltip>
                                      </InputAdornment>
                                    ),
                                  }}
                                />
                              </>
                            )}
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    )}
                  </Accordion>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}

        {analyses.includes('Multiples') && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Multiples Analysis
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Comparable Multiples Analysis:
                  </Typography>
                  <Typography variant="body2">
                    Multiples analysis compares your company to similar companies in the market.
                    Upload a CSV file with peer company data including EV/EBITDA, P/E ratios, and other relevant metrics.
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    <strong>Tip:</strong> Use the sample_comps.csv file from the project directory for testing.
                  </Typography>
                </Alert>

                <Box>
                  <input
                    accept=".csv"
                    style={{ display: 'none' }}
                    id="comps-file-upload"
                    type="file"
                    onChange={handleFileUpload}
                  />
                  <label htmlFor="comps-file-upload">
                    <Button variant="outlined" component="span">
                      Upload Comparable Companies CSV
                    </Button>
                  </label>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Upload a CSV file with peer company multiples
                  </Typography>
                  {compsFile && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      File uploaded: {compsFile.name}
                    </Alert>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {analyses.includes('Scenarios') && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Scenario Analysis
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Scenario Analysis Overview:
                  </Typography>
                  <Typography variant="body2">
                    Scenario analysis tests different "what-if" situations by overriding specific parameters.
                    This helps understand how changes in key assumptions affect your valuation.
                  </Typography>
                </Alert>

                {['Optimistic', 'Pessimistic'].map((scenario) => (
                  <Accordion key={scenario} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={!!data.scenarios[scenario]}
                            onChange={(e) => {
                              if (e.target.checked) {
                                handleScenarioChange(scenario, 'ebit_margin', 0.25);
                                handleScenarioChange(scenario, 'terminal_growth', 0.03);
                                handleScenarioChange(scenario, 'wacc', 0.09);
                              } else {
                                const newScenarios = { ...data.scenarios };
                                delete newScenarios[scenario];
                                onUpdate({ scenarios: newScenarios });
                              }
                            }}
                          />
                        }
                        label={`${scenario} Scenario`}
                      />
                    </AccordionSummary>
                    {data.scenarios[scenario] && (
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={4}>
                            <TextField
                              fullWidth
                              label="EBIT Margin (%)"
                              type="number"
                              value={((data.scenarios[scenario].ebit_margin || 0.25) * 100).toFixed(1)}
                              onChange={(e) => handleScenarioChange(scenario, 'ebit_margin', parseFloat(e.target.value) / 100)}
                              inputProps={{ min: 10, max: 35, step: 0.1 }}
                              helperText="Enter percentage (e.g., 25.0 for 25%)"
                            />
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <TextField
                              fullWidth
                              label="Terminal Growth (%)"
                              type="number"
                              value={((data.scenarios[scenario].terminal_growth || 0.03) * 100).toFixed(1)}
                              onChange={(e) => handleScenarioChange(scenario, 'terminal_growth', parseFloat(e.target.value) / 100)}
                              inputProps={{ min: -1, max: 5, step: 0.1 }}
                              helperText="Enter percentage (e.g., 3.0 for 3%)"
                            />
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <TextField
                              fullWidth
                              label="WACC (%)"
                              type="number"
                              value={((data.scenarios[scenario].wacc || 0.09) * 100).toFixed(1)}
                              onChange={(e) => handleScenarioChange(scenario, 'wacc', parseFloat(e.target.value) / 100)}
                              inputProps={{ min: 8, max: 15, step: 0.1 }}
                              helperText="Enter percentage (e.g., 9.0 for 9%)"
                            />
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    )}
                  </Accordion>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}

        {analyses.includes('Sensitivity') && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sensitivity Analysis
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Sensitivity Analysis Overview:
                  </Typography>
                  <Typography variant="body2">
                    Sensitivity analysis tests how changes in key parameters affect your valuation.
                    This helps identify which assumptions have the greatest impact on your results.
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                    <strong>Note:</strong> Select at least one parameter below to enable sensitivity analysis.
                  </Typography>
                </Alert>

                {[
                  { key: 'wacc', label: 'WACC', min: 5, max: 15, unit: '%', description: 'Weighted Average Cost of Capital' },
                  { key: 'terminal_growth', label: 'Terminal Growth', min: -2, max: 5, unit: '%', description: 'Long-term growth rate' },
                  { key: 'ebit_margin', label: 'EBIT Margin', min: 10, max: 30, unit: '%', description: 'Operating profit margin' }
                ].map((param) => (
                  <Accordion key={param.key} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={!!data.sensitivityRanges?.[param.key]}
                            onChange={(e) => handleSensitivityCheckbox(param.key, e.target.checked, param)}
                          />
                        }
                        label={`Test ${param.label} sensitivity`}
                      />
                    </AccordionSummary>
                    {data.sensitivityRanges?.[param.key] && (
                      <AccordionDetails>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {param.description}
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={3}>
                            <TextField
                              fullWidth
                              label={`Minimum (${param.unit})`}
                              type="number"
                              value={((data.sensitivityRanges[param.key].min || param.min / 100) * 100).toFixed(1)}
                              onChange={(e) => handleSensitivityChange(param.key, 'min', parseFloat(e.target.value) / 100)}
                              inputProps={{ min: param.min, max: param.max, step: 0.1 }}
                              helperText={errors[`${param.key}_min`] || `Min: ${param.min}${param.unit}`}
                              error={!!errors[`${param.key}_min`]}
                              InputProps={{
                                endAdornment: (
                                  <InputAdornment position="end">
                                    <Tooltip title="Reset to default">
                                      <IconButton
                                        size="small"
                                        onClick={() => handleSensitivityChange(param.key, 'min', param.min / 100)}
                                        edge="end"
                                      >
                                        <ClearIcon />
                                      </IconButton>
                                    </Tooltip>
                                  </InputAdornment>
                                ),
                              }}
                            />
                          </Grid>
                          <Grid item xs={12} sm={3}>
                            <TextField
                              fullWidth
                              label={`Maximum (${param.unit})`}
                              type="number"
                              value={((data.sensitivityRanges[param.key].max || param.max / 100) * 100).toFixed(1)}
                              onChange={(e) => handleSensitivityChange(param.key, 'max', parseFloat(e.target.value) / 100)}
                              inputProps={{ min: param.min, max: param.max, step: 0.1 }}
                              helperText={errors[`${param.key}_max`] || `Max: ${param.max}${param.unit}`}
                              error={!!errors[`${param.key}_max`]}
                              InputProps={{
                                endAdornment: (
                                  <InputAdornment position="end">
                                    <Tooltip title="Reset to default">
                                      <IconButton
                                        size="small"
                                        onClick={() => handleSensitivityChange(param.key, 'max', param.max / 100)}
                                        edge="end"
                                      >
                                        <ClearIcon />
                                      </IconButton>
                                    </Tooltip>
                                  </InputAdornment>
                                ),
                              }}
                            />
                          </Grid>
                          <Grid item xs={12} sm={3}>
                            <TextField
                              fullWidth
                              label="Number of Steps"
                              type="number"
                              value={data.sensitivityRanges[param.key].steps || 5}
                              onChange={(e) => handleSensitivityChange(param.key, 'steps', parseInt(e.target.value))}
                              inputProps={{ min: 3, max: 10, step: 1 }}
                              helperText={errors[`${param.key}_steps`] || "3-10 steps recommended"}
                              error={!!errors[`${param.key}_steps`]}
                              InputProps={{
                                endAdornment: (
                                  <InputAdornment position="end">
                                    <Tooltip title="Reset to default">
                                      <IconButton
                                        size="small"
                                        onClick={() => handleSensitivityChange(param.key, 'steps', 5)}
                                        edge="end"
                                      >
                                        <ClearIcon />
                                      </IconButton>
                                    </Tooltip>
                                  </InputAdornment>
                                ),
                              }}
                            />
                          </Grid>
                          <Grid item xs={12} sm={3}>
                            <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                              <Typography variant="body2" color="text.secondary">
                                <strong>Test Values:</strong>
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {(() => {
                                  const config = data.sensitivityRanges[param.key];
                                  if (!config || !config.min || !config.max || !config.steps) return 'Not configured';
                                  
                                  const values = [];
                                  for (let i = 0; i < config.steps; i++) {
                                    const value = config.min + (config.max - config.min) * (i / (config.steps - 1));
                                    values.push((value * 100).toFixed(1));
                                  }
                                  return values.join(', ');
                                })()}
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    )}
                  </Accordion>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Validation Summary */}
      {Object.keys(errors).length > 0 && (
        <Alert severity="error" sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Please fix the following issues:
          </Typography>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {Object.entries(errors).map(([field, error]) => (
              <li key={field}>{error}</li>
            ))}
          </ul>
        </Alert>
      )}
    </div>
  );
};

export default AdvancedAnalysis; 