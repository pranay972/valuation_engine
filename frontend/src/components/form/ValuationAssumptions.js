import React, { useState } from 'react';
import {
  Typography,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Alert,
  Container,
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';

const ValuationAssumptions = ({ data, onUpdate }) => {
  const [errors, setErrors] = useState({});

  const handleSliderChange = (field, value) => {
    setErrors(prev => ({ ...prev, [field]: null }));
    onUpdate({ [field]: value });
  };

  const handleNumberChange = (field, value) => {
    setErrors(prev => ({ ...prev, [field]: null }));
    
    // Allow empty input for clearing
    if (value === '') {
      onUpdate({ [field]: 0 });
      return;
    }

    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
      setErrors(prev => ({ ...prev, [field]: 'Please enter a valid number' }));
      return;
    }

    // Field-specific validation
    if (field === 'wacc' && (numValue < 0 || numValue > 1)) {
      setErrors(prev => ({ ...prev, [field]: 'WACC must be between 0% and 100%' }));
      return;
    }

    if (field === 'terminalGrowth' && (numValue < -0.1 || numValue > 0.2)) {
      setErrors(prev => ({ ...prev, [field]: 'Terminal growth must be between -10% and 20%' }));
      return;
    }

    if (field === 'taxRate' && (numValue < 0 || numValue > 1)) {
      setErrors(prev => ({ ...prev, [field]: 'Tax rate must be between 0% and 100%' }));
      return;
    }

    onUpdate({ [field]: numValue });
  };

  const handleSwitchChange = (field, checked) => {
    onUpdate({ [field]: checked });
  };

  const clearField = (field) => {
    onUpdate({ [field]: 0 });
    setErrors(prev => ({ ...prev, [field]: null }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            fontWeight: 700,
            color: 'primary.main',
            mb: 3,
            fontSize: { xs: '2rem', md: '2.5rem' },
          }}
        >
          Valuation Assumptions
        </Typography>
        <Typography 
          variant="h6" 
          color="text.secondary"
          sx={{ 
            maxWidth: 700, 
            mx: 'auto',
            lineHeight: 1.6,
            fontSize: { xs: '1rem', md: '1.1rem' },
          }}
        >
          Set key parameters that drive your valuation calculations
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ 
            borderRadius: 4,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(0, 0, 0, 0.05)',
          }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h4" gutterBottom sx={{ 
                fontWeight: 700,
                color: 'primary.main',
                mb: 4,
              }}>
                Discount Rate & Growth
              </Typography>
              
              <Box sx={{ mb: 6 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                  WACC: {(data.wacc * 100).toFixed(1)}%
                </Typography>
                <Slider
                  value={data.wacc}
                  onChange={(e, value) => handleSliderChange('wacc', value)}
                  min={0}
                  max={0.5}
                  step={0.001}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 0.1, label: '10%' },
                    { value: 0.2, label: '20%' },
                    { value: 0.3, label: '30%' },
                    { value: 0.4, label: '40%' },
                    { value: 0.5, label: '50%' }
                  ]}
                  sx={{ 
                    mb: 4,
                    '& .MuiSlider-track': {
                      height: 8,
                      borderRadius: 4,
                    },
                    '& .MuiSlider-thumb': {
                      width: 24,
                      height: 24,
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                    },
                    '& .MuiSlider-mark': {
                      width: 4,
                      height: 4,
                      borderRadius: 2,
                    },
                  }}
                />
                <TextField
                  fullWidth
                  type="number"
                  label="WACC (Manual Input)"
                  value={data.wacc || ''}
                  onChange={(e) => handleNumberChange('wacc', e.target.value)}
                  helperText={errors.wacc || "Enter WACC as decimal (e.g., 0.12 for 12%)"}
                  error={!!errors.wacc}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Tooltip title="Clear field">
                          <IconButton
                            size="large"
                            onClick={() => clearField('wacc')}
                            edge="end"
                          >
                            <ClearIcon />
                          </IconButton>
                        </Tooltip>
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>

              <Box sx={{ mb: 6 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                  Terminal Growth Rate: {(data.terminalGrowth * 100).toFixed(1)}%
                </Typography>
                <Slider
                  value={data.terminalGrowth}
                  onChange={(e, value) => handleSliderChange('terminalGrowth', value)}
                  min={-0.02}
                  max={0.1}
                  step={0.001}
                  marks={[
                    { value: -0.02, label: '-2%' },
                    { value: 0, label: '0%' },
                    { value: 0.025, label: '2.5%' },
                    { value: 0.05, label: '5%' },
                    { value: 0.075, label: '7.5%' },
                    { value: 0.1, label: '10%' }
                  ]}
                  sx={{ 
                    mb: 4,
                    '& .MuiSlider-track': {
                      height: 8,
                      borderRadius: 4,
                    },
                    '& .MuiSlider-thumb': {
                      width: 24,
                      height: 24,
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                    },
                    '& .MuiSlider-mark': {
                      width: 4,
                      height: 4,
                      borderRadius: 2,
                    },
                  }}
                />
                <TextField
                  fullWidth
                  type="number"
                  label="Terminal Growth (Manual Input)"
                  value={data.terminalGrowth || ''}
                  onChange={(e) => handleNumberChange('terminalGrowth', e.target.value)}
                  helperText={errors.terminalGrowth || "Enter growth rate as decimal (e.g., 0.025 for 2.5%)"}
                  error={!!errors.terminalGrowth}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Tooltip title="Clear field">
                          <IconButton
                            size="large"
                            onClick={() => clearField('terminalGrowth')}
                            edge="end"
                          >
                            <ClearIcon />
                          </IconButton>
                        </Tooltip>
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>

              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                  Tax Rate: {(data.taxRate * 100).toFixed(1)}%
                </Typography>
                <Slider
                  value={data.taxRate}
                  onChange={(e, value) => handleSliderChange('taxRate', value)}
                  min={0}
                  max={1}
                  step={0.01}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 0.21, label: '21%' },
                    { value: 0.35, label: '35%' },
                    { value: 0.5, label: '50%' },
                    { value: 0.75, label: '75%' },
                    { value: 1, label: '100%' }
                  ]}
                  sx={{ 
                    mb: 4,
                    '& .MuiSlider-track': {
                      height: 8,
                      borderRadius: 4,
                    },
                    '& .MuiSlider-thumb': {
                      width: 24,
                      height: 24,
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                    },
                    '& .MuiSlider-mark': {
                      width: 4,
                      height: 4,
                      borderRadius: 2,
                    },
                  }}
                />
                <TextField
                  fullWidth
                  type="number"
                  label="Tax Rate (Manual Input)"
                  value={data.taxRate || ''}
                  onChange={(e) => handleNumberChange('taxRate', e.target.value)}
                  helperText={errors.taxRate || "Enter tax rate as decimal (e.g., 0.25 for 25%)"}
                  error={!!errors.taxRate}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Tooltip title="Clear field">
                          <IconButton
                            size="large"
                            onClick={() => clearField('taxRate')}
                            edge="end"
                          >
                            <ClearIcon />
                          </IconButton>
                        </Tooltip>
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ 
            borderRadius: 4,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(0, 0, 0, 0.05)',
            height: 'fit-content',
          }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h4" gutterBottom sx={{ 
                fontWeight: 700,
                color: 'primary.main',
                mb: 4,
              }}>
                Cash Flow Timing
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={data.midYearConvention}
                    onChange={(e) => handleSwitchChange('midYearConvention', e.target.checked)}
                    size="large"
                  />
                }
                label={
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Mid-Year Convention
                  </Typography>
                }
                sx={{ mb: 3 }}
              />
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3, lineHeight: 1.6 }}>
                Check if cash flows occur mid-year (uncheck for year-end)
              </Typography>

              <Alert severity="info" sx={{ 
                borderRadius: 3,
                '& .MuiAlert-icon': {
                  fontSize: '1.5rem',
                },
              }}>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  <strong>Mid-Year Convention:</strong> Assumes cash flows occur halfway through each year, 
                  which is more realistic for most businesses. Uncheck for year-end cash flows.
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Validation Summary */}
      {Object.keys(errors).length > 0 && (
        <Alert severity="error" sx={{ mt: 4, borderRadius: 3, fontSize: '1rem' }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
            Please fix the following issues:
          </Typography>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {Object.entries(errors).map(([field, error]) => (
              <li key={field}>{error}</li>
            ))}
          </ul>
        </Alert>
      )}
    </Container>
  );
};

export default ValuationAssumptions; 