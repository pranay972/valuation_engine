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
  Chip,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

const Results = ({ results, onBack }) => {
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
    <div>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Valuation Results
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadResults}
            sx={{ mr: 1 }}
          >
            Download CSV
          </Button>
          <Button variant="contained" onClick={onBack}>
            New Analysis
          </Button>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        All values are in dollars (except price per share)
      </Alert>

      {/* Summary Results */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Summary Valuation
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Method</strong></TableCell>
                  <TableCell align="right"><strong>Enterprise Value</strong></TableCell>
                  <TableCell align="right"><strong>Equity Value</strong></TableCell>
                  <TableCell align="right"><strong>Price per Share</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.wacc_dcf && !results.wacc_dcf.error && (
                  <TableRow>
                    <TableCell>WACC DCF</TableCell>
                    <TableCell align="right">{formatCurrency(results.wacc_dcf.enterprise_value)}</TableCell>
                    <TableCell align="right">{formatCurrency(results.wacc_dcf.equity_value)}</TableCell>
                    <TableCell align="right">
                      {results.wacc_dcf.price_per_share ? formatCurrency(results.wacc_dcf.price_per_share) : 'N/A'}
                    </TableCell>
                  </TableRow>
                )}
                {results.apv_dcf && !results.apv_dcf.error && (
                  <TableRow>
                    <TableCell>APV DCF</TableCell>
                    <TableCell align="right">{formatCurrency(results.apv_dcf.enterprise_value)}</TableCell>
                    <TableCell align="right">{formatCurrency(results.apv_dcf.equity_value)}</TableCell>
                    <TableCell align="right">
                      {results.apv_dcf.price_per_share ? formatCurrency(results.apv_dcf.price_per_share) : 'N/A'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Error Display */}
      {(results.wacc_dcf?.error || results.apv_dcf?.error) && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Analysis Errors:</Typography>
          {results.wacc_dcf?.error && (
            <Typography variant="body2">WACC DCF: {results.wacc_dcf.error}</Typography>
          )}
          {results.apv_dcf?.error && (
            <Typography variant="body2">APV DCF: {results.apv_dcf.error}</Typography>
          )}
        </Alert>
      )}

      {/* Detailed Results - Each analysis gets its own section */}
      <Grid container spacing={3}>
        
        {/* DCF Analysis Details */}
        {((results.wacc_dcf && !results.wacc_dcf.error) || (results.apv_dcf && !results.apv_dcf.error)) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  DCF Analysis Details
                </Typography>
                <Grid container spacing={3}>
                  {results.wacc_dcf && !results.wacc_dcf.error && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom color="primary">
                          WACC DCF Results
                        </Typography>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary">Enterprise Value</Typography>
                          <Typography variant="h5" fontWeight="bold">
                            {formatCurrency(results.wacc_dcf.enterprise_value)}
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary">Equity Value</Typography>
                          <Typography variant="h5" fontWeight="bold">
                            {formatCurrency(results.wacc_dcf.equity_value)}
                          </Typography>
                        </Box>
                        {results.wacc_dcf.price_per_share && (
                          <Box>
                            <Typography variant="subtitle2" color="text.secondary">Price per Share</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(results.wacc_dcf.price_per_share)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  )}
                  {results.apv_dcf && !results.apv_dcf.error && (
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom color="primary">
                          APV DCF Results
                        </Typography>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary">Enterprise Value</Typography>
                          <Typography variant="h5" fontWeight="bold">
                            {formatCurrency(results.apv_dcf.enterprise_value)}
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary">Equity Value</Typography>
                          <Typography variant="h5" fontWeight="bold">
                            {formatCurrency(results.apv_dcf.equity_value)}
                          </Typography>
                        </Box>
                        {results.apv_dcf.price_per_share && (
                          <Box>
                            <Typography variant="subtitle2" color="text.secondary">Price per Share</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(results.apv_dcf.price_per_share)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Monte Carlo Results */}
        {results.monte_carlo && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monte Carlo Simulation
                </Typography>
                
                {results.monte_carlo.error ? (
                  <Alert severity="error">
                    <Typography variant="subtitle2" gutterBottom>Monte Carlo Simulation Error:</Typography>
                    <Typography variant="body2">{results.monte_carlo.error}</Typography>
                    {results.monte_carlo.error.includes("terminal growth >= WACC") && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Try adjusting the variable specifications to ensure terminal growth is always less than WACC.
                      </Typography>
                    )}
                  </Alert>
                ) : (
                  <Grid container spacing={3}>
                    {Object.keys(results.monte_carlo).map((method) => {
                      const methodData = results.monte_carlo[method];
                      if (!methodData || !methodData.statistics) return null;
                      
                      const stats = methodData.statistics;
                      return (
                        <Grid item xs={12} md={6} key={method}>
                          <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
                            <Typography variant="h6" gutterBottom color="primary">
                              {method} DCF Distribution Statistics
                            </Typography>
                            
                            <Grid container spacing={2}>
                              <Grid item xs={6}>
                                <Typography variant="subtitle2" color="text.secondary">Mean EV</Typography>
                                <Typography variant="h6" fontWeight="bold">
                                  {formatCurrency(stats.EV?.mean || 0)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="subtitle2" color="text.secondary">Std Dev EV</Typography>
                                <Typography variant="h6" fontWeight="bold">
                                  {formatCurrency(stats.EV?.std || 0)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="subtitle2" color="text.secondary">5th Percentile</Typography>
                                <Typography variant="h6" fontWeight="bold">
                                  {formatCurrency(stats.EV?.['5%'] || 0)}
                                </Typography>
                              </Grid>
                              <Grid item xs={6}>
                                <Typography variant="subtitle2" color="text.secondary">95th Percentile</Typography>
                                <Typography variant="h6" fontWeight="bold">
                                  {formatCurrency(stats.EV?.['95%'] || 0)}
                                </Typography>
                              </Grid>
                            </Grid>
                            
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                Confidence Intervals
                              </Typography>
                              <Grid container spacing={1}>
                                {[5, 25, 50, 75, 95].map((p) => (
                                  <Grid item xs={4} key={p}>
                                    <Chip 
                                      label={`${p}%: ${formatCurrency(stats.EV?.[`${p}%`] || 0)}`}
                                      size="small"
                                      variant="outlined"
                                    />
                                  </Grid>
                                ))}
                              </Grid>
                            </Box>
                          </Box>
                        </Grid>
                      );
                    })}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Scenario Analysis */}
        {results.scenarios && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Scenario Analysis
                </Typography>
                
                {results.scenarios.error ? (
                  <Alert severity="error">
                    {results.scenarios.error}
                  </Alert>
                ) : (
                  <Grid container spacing={3}>
                    {Array.isArray(results.scenarios) && results.scenarios.map((scenario, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                          <Typography variant="h6" gutterBottom color="primary">
                            {scenario.scenario_name || `Scenario ${index + 1}`}
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">Enterprise Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(scenario.EV || 0)}
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">Equity Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(scenario.Equity || 0)}
                            </Typography>
                          </Box>
                          {scenario.PS && (
                            <Box>
                              <Typography variant="subtitle2" color="text.secondary">Price per Share</Typography>
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

        {/* Sensitivity Analysis */}
        {results.sensitivity && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sensitivity Analysis
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
                ) : (
                  <Grid container spacing={3}>
                    {Array.isArray(results.sensitivity) && results.sensitivity.slice(0, 6).map((result, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                          <Typography variant="h6" gutterBottom color="primary">
                            {result.parameter || `Parameter ${index + 1}`}
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {typeof result.value === 'number' ? formatPercentage(result.value) : result.value}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="subtitle2" color="text.secondary">Enterprise Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(result.EV || 0)}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                    ))}
                    {results.sensitivity.length > 6 && (
                      <Grid item xs={12}>
                        <Alert severity="info">
                          Showing first 6 results. Total: {results.sensitivity.length} sensitivity points analyzed.
                        </Alert>
                      </Grid>
                    )}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Multiples Analysis */}
        {results.multiples && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
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
                  <Grid container spacing={3}>
                    {results.multiples.map((multiple, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Box sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                          <Typography variant="h6" gutterBottom color="primary">
                            {multiple.metric || `Multiple ${index + 1}`}
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">Enterprise Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(multiple.EV || 0)}
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">Equity Value</Typography>
                            <Typography variant="h5" fontWeight="bold">
                              {formatCurrency(multiple.Equity || 0)}
                            </Typography>
                          </Box>
                          {multiple.PS && (
                            <Box>
                              <Typography variant="subtitle2" color="text.secondary">Price per Share</Typography>
                              <Typography variant="h5" fontWeight="bold">
                                {formatCurrency(multiple.PS)}
                              </Typography>
                            </Box>
                          )}
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
    </div>
  );
};

export default Results; 