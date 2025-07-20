import React, { useState } from 'react';
import {
  Typography,
  Grid,
  TextField,
  Slider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Box,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  InputAdornment,
  IconButton,
  Tooltip,
  Container,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ClearIcon from '@mui/icons-material/Clear';

const FinancialProjections = ({ data, onUpdate }) => {
  const [errors, setErrors] = useState({});

  // Ensure data has all required properties with defaults
  const safeData = {
    inputMode: data?.inputMode || 'driver',
    revenue: data?.revenue || [],
    ebitMargin: data?.ebitMargin || 0.20,
    capex: data?.capex || [],
    depreciation: data?.depreciation || [],
    nwcChanges: data?.nwcChanges || [],
    fcfSeries: data?.fcfSeries || [],
    shareCount: data?.shareCount || 100000000,
    costOfDebt: data?.costOfDebt || 0.05,
    currentDebt: data?.currentDebt || 0,
    debtSchedule: data?.debtSchedule || {},
  };

  const handleInputModeChange = (event) => {
    onUpdate({ inputMode: event.target.value });
  };

  // Improved series handling with validation
  const handleSeriesChange = (field, value) => {
    // Clear any existing errors for this field
    setErrors(prev => ({ ...prev, [field]: null }));
    
    // Handle empty input
    if (!value.trim()) {
      onUpdate({ [field]: [] });
      return;
    }

    try {
      const numbers = value.split(',').map(x => {
        const trimmed = x.trim();
        if (!trimmed) return null;
        const parsed = parseFloat(trimmed);
        if (isNaN(parsed)) {
          throw new Error(`Invalid number: ${trimmed}`);
        }
        return parsed;
      }).filter(x => x !== null);

      // Validate series length consistency
      if (field === 'revenue' && numbers.length > 0) {
        const otherSeries = ['capex', 'depreciation', 'nwcChanges'];
        otherSeries.forEach(otherField => {
          if (safeData[otherField] && safeData[otherField].length > 0 && 
              safeData[otherField].length !== numbers.length) {
            setErrors(prev => ({ 
              ...prev, 
              [field]: `Series length (${numbers.length}) doesn't match ${otherField} (${safeData[otherField].length})` 
            }));
          }
        });
      }

      onUpdate({ [field]: numbers });
    } catch (error) {
      setErrors(prev => ({ ...prev, [field]: error.message }));
    }
  };

  // Improved number input handling
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
    if (field === 'shareCount' && numValue <= 0) {
      setErrors(prev => ({ ...prev, [field]: 'Share count must be positive' }));
      return;
    }

    if (field === 'costOfDebt' && (numValue < 0 || numValue > 1)) {
      setErrors(prev => ({ ...prev, [field]: 'Cost of debt must be between 0% and 100%' }));
      return;
    }

    if (field === 'currentDebt' && numValue < 0) {
      setErrors(prev => ({ ...prev, [field]: 'Current debt cannot be negative' }));
      return;
    }

    onUpdate({ [field]: numValue });
  };

  const handleSliderChange = (field, value) => {
    onUpdate({ [field]: value });
  };

  const formatSeries = (series) => {
    if (!Array.isArray(series) || series.length === 0) return '';
    return series.join(', ');
  };

  const handleDebtScheduleChange = (year, value) => {
    const newDebtSchedule = { ...(safeData.debtSchedule || {}) };
    if (value > 0) {
      newDebtSchedule[year] = value;
    } else {
      delete newDebtSchedule[year];
    }
    onUpdate({ debtSchedule: newDebtSchedule });
  };

  const clearField = (field) => {
    onUpdate({ [field]: field === 'shareCount' ? 0 : [] });
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
          Financial Projections
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
          Define your company's financial projections and capital structure
        </Typography>
      </Box>

      <FormControl component="fieldset" sx={{ mb: 5, width: '100%' }}>
        <FormLabel component="legend" sx={{ fontSize: '1.2rem', fontWeight: 600, mb: 2 }}>
          Choose input method:
        </FormLabel>
        <RadioGroup
          value={safeData.inputMode}
          onChange={handleInputModeChange}
          sx={{ 
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 3,
          }}
        >
          <FormControlLabel 
            value="driver" 
            control={<Radio size="large" />} 
            label={
              <Box>
                <Typography variant="h6" fontWeight={600}>Driver-based (Revenue/Margins)</Typography>
                <Typography variant="body2" color="text.secondary">
                  Build projections from revenue growth and margin assumptions
                </Typography>
              </Box>
            }
            sx={{ 
              flex: 1,
              p: 3,
              border: '2px solid',
              borderColor: safeData.inputMode === 'driver' ? 'primary.main' : 'grey.200',
              borderRadius: 3,
              bgcolor: safeData.inputMode === 'driver' ? 'primary.50' : 'transparent',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'primary.50',
              },
            }}
          />
          <FormControlLabel 
            value="direct" 
            control={<Radio size="large" />} 
            label={
              <Box>
                <Typography variant="h6" fontWeight={600}>Direct FCF Series</Typography>
                <Typography variant="body2" color="text.secondary">
                  Enter free cash flow projections directly
                </Typography>
              </Box>
            }
            sx={{ 
              flex: 1,
              p: 3,
              border: '2px solid',
              borderColor: safeData.inputMode === 'direct' ? 'primary.main' : 'grey.200',
              borderRadius: 3,
              bgcolor: safeData.inputMode === 'direct' ? 'primary.50' : 'transparent',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'primary.50',
              },
            }}
          />
        </RadioGroup>
      </FormControl>

      <Grid container spacing={4}>
        {safeData.inputMode === 'driver' ? (
          <>
            <Grid item xs={12}>
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
                    Revenue & Operating Metrics
                  </Typography>
                  
                  <TextField
                    fullWidth
                    label="Revenue Series (comma-separated)"
                    value={formatSeries(safeData.revenue)}
                    onChange={(e) => handleSeriesChange('revenue', e.target.value)}
                    helperText={errors.revenue || "Enter projected revenues for each year, separated by commas"}
                    error={!!errors.revenue}
                    sx={{ mb: 4 }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('revenue')}
                              edge="end"
                            >
                              <ClearIcon />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <Box sx={{ mb: 5 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                      EBIT Margin: {(safeData.ebitMargin * 100).toFixed(1)}%
                    </Typography>
                    <Slider
                      value={safeData.ebitMargin}
                      onChange={(e, value) => handleSliderChange('ebitMargin', value)}
                      min={0}
                      max={1}
                      step={0.01}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 0.25, label: '25%' },
                        { value: 0.5, label: '50%' },
                        { value: 0.75, label: '75%' },
                        { value: 1, label: '100%' }
                      ]}
                      sx={{ 
                        mb: 3,
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
                  </Box>

                  <TextField
                    fullWidth
                    label="Capital Expenditure Series"
                    value={formatSeries(safeData.capex)}
                    onChange={(e) => handleSeriesChange('capex', e.target.value)}
                    helperText={errors.capex || "Enter projected CapEx for each year"}
                    error={!!errors.capex}
                    sx={{ mb: 4 }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('capex')}
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
                    label="Depreciation Series"
                    value={formatSeries(safeData.depreciation)}
                    onChange={(e) => handleSeriesChange('depreciation', e.target.value)}
                    helperText={errors.depreciation || "Enter projected depreciation for each year"}
                    error={!!errors.depreciation}
                    sx={{ mb: 4 }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('depreciation')}
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
                    label="Net Working Capital Changes"
                    value={formatSeries(safeData.nwcChanges)}
                    onChange={(e) => handleSeriesChange('nwcChanges', e.target.value)}
                    helperText={errors.nwcChanges || "Enter projected NWC changes for each year"}
                    error={!!errors.nwcChanges}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('nwcChanges')}
                              edge="end"
                            >
                              <ClearIcon />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
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
                    Capital Structure
                  </Typography>
                  
                  <TextField
                    fullWidth
                    type="number"
                    label="Number of Shares Outstanding"
                    value={safeData.shareCount || ''}
                    onChange={(e) => handleNumberChange('shareCount', e.target.value)}
                    helperText={errors.shareCount || "Enter the total number of shares"}
                    error={!!errors.shareCount}
                    sx={{ mb: 4 }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('shareCount')}
                              edge="end"
                            >
                              <ClearIcon />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <Box sx={{ mb: 5 }}>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                      Cost of Debt: {(safeData.costOfDebt * 100).toFixed(1)}%
                    </Typography>
                    <Slider
                      value={safeData.costOfDebt}
                      onChange={(e, value) => onUpdate({ costOfDebt: value })}
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
                        mb: 3,
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
                  </Box>

                  <TextField
                    fullWidth
                    type="number"
                    label="Current Debt"
                    value={safeData.currentDebt || ''}
                    onChange={(e) => handleNumberChange('currentDebt', e.target.value)}
                    helperText={errors.currentDebt || "Enter the company's current debt level"}
                    error={!!errors.currentDebt}
                    sx={{ mb: 4 }}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Clear field">
                            <IconButton
                              size="large"
                              onClick={() => clearField('currentDebt')}
                              edge="end"
                            >
                              <ClearIcon />
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <Accordion sx={{ 
                    borderRadius: 3,
                    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                  }}>
                    <AccordionSummary 
                      expandIcon={<ExpandMoreIcon />}
                      sx={{ px: 3, py: 2 }}
                    >
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Advanced Debt Schedule (Optional)
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails sx={{ px: 3, pb: 3 }}>
                      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                        Specify debt levels for each year. Leave empty to use terminal debt assumption. 
                        Current debt will be used as the starting point for Year 1 if not specified.
                      </Typography>
                      
                      <Grid container spacing={3}>
                        {[1, 2, 3, 4, 5].map((year) => (
                          <Grid item xs={12} sm={6} md={4} key={year}>
                            <TextField
                              fullWidth
                              type="number"
                              label={`Year ${year} Debt`}
                              value={(safeData.debtSchedule && safeData.debtSchedule[year]) || ''}
                              onChange={(e) => handleDebtScheduleChange(year, parseFloat(e.target.value) || 0)}
                              helperText={`Debt level in year ${year}`}
                              InputProps={{
                                startAdornment: <InputAdornment position="start">$</InputAdornment>,
                              }}
                            />
                          </Grid>
                        ))}
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                </CardContent>
              </Card>
            </Grid>
          </>
        ) : (
          <Grid item xs={12}>
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
                  Direct FCF Series
                </Typography>
                
                <TextField
                  fullWidth
                  label="Free Cash Flow Series (comma-separated)"
                  value={formatSeries(safeData.fcfSeries)}
                  onChange={(e) => handleSeriesChange('fcfSeries', e.target.value)}
                  helperText={errors.fcfSeries || "Enter projected free cash flows for each year, separated by commas"}
                  error={!!errors.fcfSeries}
                  multiline
                  rows={4}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Tooltip title="Clear field">
                          <IconButton
                            size="large"
                            onClick={() => clearField('fcfSeries')}
                            edge="end"
                          >
                            <ClearIcon />
                          </IconButton>
                        </Tooltip>
                      </InputAdornment>
                    ),
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        )}
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

export default FinancialProjections; 