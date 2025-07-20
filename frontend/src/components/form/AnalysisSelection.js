import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  FormControlLabel,
  Checkbox,
  Grid,
  Alert,
} from '@mui/material';

const AnalysisSelection = ({ analyses, onUpdate }) => {
  const analysisOptions = [
    { key: 'WACC DCF', label: 'WACC DCF', description: 'Standard DCF using WACC' },
    { key: 'APV DCF', label: 'APV DCF', description: 'Adjusted Present Value method' },
    { key: 'Monte Carlo', label: 'Monte Carlo', description: 'Uncertainty analysis' },
    { key: 'Multiples', label: 'Comparable Multiples', description: 'Peer company analysis' },
    { key: 'Scenarios', label: 'Scenario Analysis', description: 'What-if scenarios' },
    { key: 'Sensitivity', label: 'Sensitivity Analysis', description: 'Parameter sensitivity' },
  ];

  const handleChange = (analysisKey) => {
    const newAnalyses = analyses.includes(analysisKey)
      ? analyses.filter(a => a !== analysisKey)
      : [...analyses, analysisKey];
    onUpdate(newAnalyses);
  };

  return (
    <div>
      <Typography variant="h2" gutterBottom>
        Select Analyses
      </Typography>
      
      {analyses.length === 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please select at least one analysis type.
        </Alert>
      )}

      <Grid container spacing={2}>
        {analysisOptions.map((option) => (
          <Grid item xs={12} md={6} key={option.key}>
            <Card 
              variant="outlined" 
              sx={{ 
                cursor: 'pointer',
                borderColor: analyses.includes(option.key) ? 'primary.main' : 'grey.300',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => handleChange(option.key)}
            >
              <CardContent>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={analyses.includes(option.key)}
                      onChange={() => handleChange(option.key)}
                    />
                  }
                  label={
                    <div>
                      <Typography variant="h6">{option.label}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {option.description}
                      </Typography>
                    </div>
                  }
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default AnalysisSelection; 