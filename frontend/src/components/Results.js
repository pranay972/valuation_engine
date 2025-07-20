import React from 'react';
import {
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  Box,
  Alert,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

const Results = ({ results, onBack }) => {
  // Call debug function on component mount
  React.useEffect(() => {
    const debugData = () => {
      console.log('🔍 DEBUG: Raw results data received:', results);
      console.log('🔍 DEBUG: Results keys:', Object.keys(results || {}));
      
      if (results) {
        Object.keys(results).forEach(key => {
          console.log(`🔍 DEBUG: ${key}:`, results[key]);
          if (results[key] && typeof results[key] === 'object') {
            console.log(`🔍 DEBUG: ${key} keys:`, Object.keys(results[key]));
          }
        });
      }
    };
    
    debugData();
  }, [results]);

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const downloadResults = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Method,Enterprise Value,Equity Value,Price per Share\n";
    if (results.wacc_dcf && !results.wacc_dcf.error) {
      csvContent += `WACC DCF,${results.wacc_dcf.enterprise_value},${results.wacc_dcf.equity_value},${results.wacc_dcf.price_per_share || 'N/A'}\n`;
    }
    if (results.apv_dcf && !results.apv_dcf.error) {
      csvContent += `APV DCF,${results.apv_dcf.enterprise_value},${results.apv_dcf.equity_value},${results.apv_dcf.price_per_share || 'N/A'}\n`;
    }
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `valuation_results_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };



  if (!results) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h4" gutterBottom>
          No Results Available
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Run a valuation analysis to see results here.
        </Typography>
        <Button variant="contained" onClick={onBack} sx={{ mt: 2 }}>
          Back to Form
        </Button>
      </Box>
    );
  }

  const hasValidResults = (results.wacc_dcf && !results.wacc_dcf.error) || 
                         (results.apv_dcf && !results.apv_dcf.error) ||
                         results.monte_carlo || results.scenarios || results.sensitivity;

  if (!hasValidResults) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h4" gutterBottom>
          No Valid Results Available
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          The valuation analysis did not produce valid results.
        </Typography>
        <Button variant="contained" onClick={onBack}>
          Back to Form
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: '100%', mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
          Valuation Results
        </Typography>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={downloadResults}
          sx={{ mr: 2 }}
        >
          Download CSV
        </Button>
        <Button
          variant="contained"
          onClick={onBack}
        >
          Back to Form
        </Button>
      </Box>

      <Grid container spacing={4}>
        {/* DCF Results */}
        {(results.wacc_dcf || results.apv_dcf) && (
          <Grid item xs={12}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }} className="card-hover">
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h4" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 700,
                    color: 'primary.main',
                    mb: 4,
                  }}
                >
                  DCF Valuation Results
                </Typography>
                
                <Grid container spacing={4}>
                  {results.wacc_dcf && !results.wacc_dcf.error && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ 
                        p: 4, 
                        bgcolor: 'primary.50', 
                        borderRadius: 3,
                        border: '2px solid',
                        borderColor: 'primary.200',
                        height: '100%',
                      }}>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
                          WACC DCF
                        </Typography>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" color="text.secondary">Enterprise Value</Typography>
                          <Typography variant="h4" fontWeight="bold" color="primary.main">
                            {formatCurrency(results.wacc_dcf.enterprise_value)}
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" color="text.secondary">Equity Value</Typography>
                          <Typography variant="h4" fontWeight="bold">
                            {formatCurrency(results.wacc_dcf.equity_value)}
                          </Typography>
                        </Box>
                        {results.wacc_dcf.price_per_share && (
                          <Box>
                            <Typography variant="subtitle1" color="text.secondary">Price per Share</Typography>
                            <Typography variant="h4" fontWeight="bold">
                              {formatCurrency(results.wacc_dcf.price_per_share)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  )}
                  
                  {results.apv_dcf && !results.apv_dcf.error && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ 
                        p: 4, 
                        bgcolor: 'success.50', 
                        borderRadius: 3,
                        border: '2px solid',
                        borderColor: 'success.200',
                        height: '100%',
                      }}>
                        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: 'success.main' }}>
                          APV DCF
                        </Typography>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" color="text.secondary">Enterprise Value</Typography>
                          <Typography variant="h4" fontWeight="bold" color="success.main">
                            {formatCurrency(results.apv_dcf.enterprise_value)}
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                          <Typography variant="subtitle1" color="text.secondary">Equity Value</Typography>
                          <Typography variant="h4" fontWeight="bold">
                            {formatCurrency(results.apv_dcf.equity_value)}
                          </Typography>
                        </Box>
                        {results.apv_dcf.price_per_share && (
                          <Box>
                            <Typography variant="subtitle1" color="text.secondary">Price per Share</Typography>
                            <Typography variant="h4" fontWeight="bold">
                              {formatCurrency(results.apv_dcf.price_per_share)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  )}
                </Grid>
                
                {(results.wacc_dcf?.error || results.apv_dcf?.error) && (
                  <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>DCF Calculation Error:</Typography>
                    <Typography variant="body2">
                      {results.wacc_dcf?.error || results.apv_dcf?.error}
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Monte Carlo Analysis - FULL WIDTH */}
        {results.monte_carlo && (
          <Grid item xs={12}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }} className="card-hover">
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h4" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 700,
                    color: 'primary.main',
                    mb: 4,
                  }}
                >
                  Monte Carlo Analysis Results
                </Typography>
                
                {results.monte_carlo.error ? (
                  <Alert severity="error">
                    <Typography variant="subtitle2" gutterBottom>Monte Carlo Error:</Typography>
                    <Typography variant="body2">{results.monte_carlo.error}</Typography>
                  </Alert>
                ) : Array.isArray(results.monte_carlo) && results.monte_carlo.length > 0 ? (
                  <>
                    {results.monte_carlo.map((methodData, methodIndex) => {
                      const data = methodData.data || methodData;
                      const method = methodData.method || `Method ${methodIndex + 1}`;
                      
                      // Calculate statistics
                      const evValues = data.map(item => item.EV).filter(v => v !== null && v !== undefined);
                      const stats = {
                        mean: evValues.length > 0 ? evValues.reduce((a, b) => a + b, 0) / evValues.length : 0,
                        median: evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length / 2)] : 0,
                        min: evValues.length > 0 ? Math.min(...evValues) : 0,
                        max: evValues.length > 0 ? Math.max(...evValues) : 0,
                        count: evValues.length,
                        EV: {
                          mean: evValues.length > 0 ? evValues.reduce((a, b) => a + b, 0) / evValues.length : 0,
                          median: evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length / 2)] : 0,
                          min: evValues.length > 0 ? Math.min(...evValues) : 0,
                          max: evValues.length > 0 ? Math.max(...evValues) : 0,
                          '5%': evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length * 0.05)] : 0,
                          '25%': evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length * 0.25)] : 0,
                          '75%': evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length * 0.75)] : 0,
                          '95%': evValues.length > 0 ? evValues.sort((a, b) => a - b)[Math.floor(evValues.length * 0.95)] : 0,
                        }
                      };

                      return (
                        <Box key={methodIndex} sx={{ mb: 6 }}>
                          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                            {method}
                          </Typography>
                          
                          {/* Statistics Table */}
                          <Grid container spacing={4} sx={{ mb: 4 }}>
                            <Grid item xs={12} md={6}>
                              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                                Summary Statistics
                              </Typography>
                              <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                                <Table>
                                  <TableHead>
                                    <TableRow>
                                      <TableCell sx={{ fontWeight: 600 }}>Metric</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>Enterprise Value</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    <TableRow>
                                      <TableCell>Mean</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(stats.EV?.mean || 0)}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell>Median</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(stats.EV?.median || 0)}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell>Minimum</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(stats.EV?.min || 0)}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell>Maximum</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(stats.EV?.max || 0)}</TableCell>
                                    </TableRow>
                                    <TableRow>
                                      <TableCell>Simulations</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>{stats.count || data.length}</TableCell>
                                    </TableRow>
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </Grid>
                            
                            <Grid item xs={12} md={6}>
                              {/* Confidence Intervals Table */}
                              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                                Confidence Intervals
                              </Typography>
                              <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                                <Table>
                                  <TableHead>
                                    <TableRow>
                                      <TableCell sx={{ fontWeight: 600 }}>Percentile</TableCell>
                                      <TableCell sx={{ fontWeight: 600 }}>Enterprise Value</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {[5, 25, 75, 95].map((p) => (
                                      <TableRow key={p}>
                                        <TableCell>{p}%</TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(stats.EV?.[`${p}%`] || 0)}</TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </Grid>
                          </Grid>
                        </Box>
                      );
                    })}
                  </>
                ) : (
                  <Alert severity="info">
                    No Monte Carlo results available. Please configure Monte Carlo parameters in the Advanced Analysis section.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Sensitivity Analysis - FULL WIDTH */}
        {results.sensitivity && (
          <Grid item xs={12}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }} className="card-hover">
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h4" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 700,
                    color: 'primary.main',
                    mb: 4,
                  }}
                >
                  Sensitivity Analysis Results
                </Typography>
                
                {results.sensitivity.error ? (
                  <Alert severity="error">
                    <Typography variant="subtitle2" gutterBottom>Sensitivity Analysis Error:</Typography>
                    <Typography variant="body2">{results.sensitivity.error}</Typography>
                    {results.sensitivity.error.includes("No sensitivity ranges configured") && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Please configure sensitivity parameters in the Advanced Analysis section.
                      </Typography>
                    )}
                  </Alert>
                ) : Array.isArray(results.sensitivity) && results.sensitivity.length > 0 ? (
                  <>
                    {/* Clean Sensitivity Data Table */}
                    <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ fontWeight: 600 }}>Parameter</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Value</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Enterprise Value</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {results.sensitivity.map((result, index) => (
                            <TableRow key={index} hover>
                              <TableCell>{result.parameter}</TableCell>
                              <TableCell>
                                {typeof result.value === 'number' ? formatPercentage(result.value) : result.value}
                              </TableCell>
                              <TableCell sx={{ fontWeight: 600 }}>
                                {formatCurrency(result.EV || 0)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                ) : (
                  <Alert severity="info">
                    No sensitivity results available. Please configure sensitivity parameters in the Advanced Analysis section.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Scenario Analysis - FULL WIDTH */}
        {results.scenarios && (
          <Grid item xs={12}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }} className="card-hover">
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h4" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 700,
                    color: 'primary.main',
                    mb: 4,
                  }}
                >
                  Scenario Analysis Results
                </Typography>
                
                {results.scenarios.error ? (
                  <Alert severity="error">
                    {results.scenarios.error}
                  </Alert>
                ) : (
                  <Grid container spacing={4}>
                    {Array.isArray(results.scenarios) && results.scenarios.map((scenario, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box sx={{ 
                          p: 4, 
                          bgcolor: 'grey.50', 
                          borderRadius: 3,
                          border: '1px solid',
                          borderColor: 'grey.200',
                          height: '100%',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
                          },
                        }}>
                          <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
                            {scenario.scenario_name || `Scenario ${index + 1}`}
                          </Typography>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" color="text.secondary">Enterprise Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(scenario.EV || 0)}
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" color="text.secondary">Equity Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(scenario.Equity || 0)}
                            </Typography>
                          </Box>
                          {scenario.PS && (
                            <Box>
                              <Typography variant="subtitle1" color="text.secondary">Price per Share</Typography>
                              <Typography variant="h5" fontWeight="bold">
                                {formatCurrency(scenario.PS)}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Multiples Analysis - FULL WIDTH */}
        {results.multiples && (
          <Grid item xs={12}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }} className="card-hover">
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h4" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 700,
                    color: 'primary.main',
                    mb: 4,
                  }}
                >
                  Comparable Multiples Analysis
                </Typography>
                
                {results.multiples.error ? (
                  <Alert severity="error">
                    <Typography variant="subtitle2" gutterBottom>Multiples Analysis Error:</Typography>
                    <Typography variant="body2">{results.multiples.error}</Typography>
                    {results.multiples.error.includes("No comparable companies data provided") && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Please upload a CSV file with peer company multiples in the Advanced Analysis section.
                      </Typography>
                    )}
                  </Alert>
                ) : Array.isArray(results.multiples) && results.multiples.length > 0 ? (
                  <Grid container spacing={4}>
                    {results.multiples.map((multiple, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box sx={{ 
                          p: 4, 
                          bgcolor: 'grey.50', 
                          borderRadius: 3,
                          border: '1px solid',
                          borderColor: 'grey.200',
                          height: '100%',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
                          },
                        }}>
                          <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
                            {multiple.Multiple || multiple.metric || `Multiple ${index + 1}`}
                          </Typography>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" color="text.secondary">Mean Implied EV</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(multiple['Mean Implied EV'] || multiple.EV || 0)}
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" color="text.secondary">Mean Multiple</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {multiple['Mean Multiple'] || multiple.multiple || 'N/A'}
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" color="text.secondary">Our Metric</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(multiple['Our Metric'] || multiple.metric || 0)}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Alert severity="info">
                    Multiples analysis requires file upload. Please upload a comparable companies CSV file in the Advanced Analysis section.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Results; 