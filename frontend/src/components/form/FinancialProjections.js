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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const FinancialProjections = ({ data, onUpdate }) => {
  const [debtInputMethod, setDebtInputMethod] = useState('simple');

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
    debtSchedule: data?.debtSchedule || {},
  };

  const handleInputModeChange = (event) => {
    onUpdate({ inputMode: event.target.value });
  };

  const handleSeriesChange = (field, value) => {
    const numbers = value.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
    onUpdate({ [field]: numbers });
  };

  const handleSliderChange = (field, value) => {
    onUpdate({ [field]: value });
  };

  const formatSeries = (series) => {
    if (!Array.isArray(series)) return '';
    return series.join(', ');
  };

  const handleDebtScheduleChange = (year, value) => {
    const newDebtSchedule = { ...safeData.debtSchedule };
    if (value > 0) {
      newDebtSchedule[year] = value;
    } else {
      delete newDebtSchedule[year];
    }
    onUpdate({ debtSchedule: newDebtSchedule });
  };

  // Removed unused function getDebtScheduleArray

  return (
    <div>
      <Typography variant="h2" gutterBottom>
        Financial Projections
      </Typography>

      <FormControl component="fieldset" sx={{ mb: 3 }}>
        <FormLabel component="legend">Choose input method:</FormLabel>
        <RadioGroup
          value={safeData.inputMode}
          onChange={handleInputModeChange}
        >
          <FormControlLabel 
            value="driver" 
            control={<Radio />} 
            label="Driver-based (Revenue/Margins)" 
          />
          <FormControlLabel 
            value="direct" 
            control={<Radio />} 
            label="Direct FCF Series" 
          />
        </RadioGroup>
      </FormControl>

      <Grid container spacing={3}>
        {safeData.inputMode === 'driver' ? (
          <>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Revenue & Operating Metrics
                  </Typography>
                  
                  <TextField
                    fullWidth
                    label="Revenue Series (comma-separated)"
                    value={formatSeries(safeData.revenue)}
                    onChange={(e) => handleSeriesChange('revenue', e.target.value)}
                    helperText="Enter projected revenues for each year, separated by commas"
                    sx={{ mb: 2 }}
                  />

                  <Typography gutterBottom>
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
                      { value: 0.5, label: '50%' },
                      { value: 1, label: '100%' }
                    ]}
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Capital Expenditure Series"
                    value={formatSeries(safeData.capex)}
                    onChange={(e) => handleSeriesChange('capex', e.target.value)}
                    helperText="Enter projected CapEx for each year"
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Depreciation Series"
                    value={formatSeries(safeData.depreciation)}
                    onChange={(e) => handleSeriesChange('depreciation', e.target.value)}
                    helperText="Enter projected depreciation for each year"
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Net Working Capital Changes"
                    value={formatSeries(safeData.nwcChanges)}
                    onChange={(e) => handleSeriesChange('nwcChanges', e.target.value)}
                    helperText="Enter projected NWC changes for each year"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Capital Structure
                  </Typography>
                  
                  <TextField
                    fullWidth
                    type="number"
                    label="Number of Shares Outstanding"
                    value={safeData.shareCount}
                    onChange={(e) => onUpdate({ shareCount: parseFloat(e.target.value) })}
                    helperText="Enter the total number of shares"
                    sx={{ mb: 2 }}
                  />

                  <Box sx={{ mb: 3 }}>
                    <Typography gutterBottom>
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
                        { value: 0.2, label: '20%' }
                      ]}
                    />
                  </Box>

                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="h6">Debt Schedule (Optional)</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Debt Schedule shows how much debt the company has each year.
                        Year 0 = Current debt (today), Year 1 = Debt at end of year 1, etc.
                      </Typography>
                      
                      <FormControl component="fieldset" sx={{ mb: 2 }}>
                        <RadioGroup
                          value={debtInputMethod}
                          onChange={(e) => setDebtInputMethod(e.target.value)}
                        >
                          <FormControlLabel 
                            value="simple" 
                            control={<Radio />} 
                            label="Simple (Current debt only)" 
                          />
                          <FormControlLabel 
                            value="multi" 
                            control={<Radio />} 
                            label="Multi-year schedule" 
                          />
                        </RadioGroup>
                      </FormControl>

                      {debtInputMethod === 'simple' ? (
                        <TextField
                          fullWidth
                          type="number"
                          label="Current Debt ($)"
                          value={safeData.debtSchedule[0] || 0}
                          onChange={(e) => handleDebtScheduleChange(0, parseFloat(e.target.value))}
                          helperText="Enter the total debt in dollars"
                        />
                      ) : (
                        <Grid container spacing={2}>
                          {Array.from({ length: Math.max(5, safeData.revenue.length) }, (_, i) => (
                            <Grid item xs={6} sm={4} md={3} key={i}>
                              <TextField
                                fullWidth
                                type="number"
                                label={i === 0 ? "Today" : `Year ${i}`}
                                value={safeData.debtSchedule[i] || 0}
                                onChange={(e) => handleDebtScheduleChange(i, parseFloat(e.target.value))}
                                size="small"
                              />
                            </Grid>
                          ))}
                        </Grid>
                      )}

                      {Object.keys(safeData.debtSchedule).length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Your Debt Schedule:
                          </Typography>
                          <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Year</TableCell>
                                  <TableCell align="right">Debt ($)</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {Object.entries(safeData.debtSchedule)
                                  .filter(([_, value]) => value > 0)
                                  .map(([year, value]) => (
                                    <TableRow key={year}>
                                      <TableCell>{year === '0' ? 'Today' : `Year ${year}`}</TableCell>
                                      <TableCell align="right">${value.toLocaleString()}</TableCell>
                                    </TableRow>
                                  ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </Box>
                      )}
                    </AccordionDetails>
                  </Accordion>
                </CardContent>
              </Card>
            </Grid>
          </>
        ) : (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Direct FCF Input
                </Typography>
                
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Free Cash Flow Series (comma-separated)"
                  value={formatSeries(safeData.fcfSeries)}
                  onChange={(e) => handleSeriesChange('fcfSeries', e.target.value)}
                  helperText="Enter projected free cash flows for each year, separated by commas"
                />
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </div>
  );
};

export default FinancialProjections; 