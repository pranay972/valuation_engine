import React from 'react';
import {
  Typography,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  Box,
} from '@mui/material';

const ValuationAssumptions = ({ data, onUpdate }) => {
  const handleSliderChange = (field, value) => {
    onUpdate({ [field]: value });
  };

  const handleSwitchChange = (field, checked) => {
    onUpdate({ [field]: checked });
  };

  return (
    <div>
      <Typography variant="h2" gutterBottom>
        Valuation Assumptions
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Discount Rate & Growth
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
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
                    { value: 0.2, label: '20%' }
                  ]}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
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
                    { value: 0.05, label: '5%' }
                  ]}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
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
                    { value: 0.5, label: '50%' }
                  ]}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cash Flow Timing
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={data.midYearConvention}
                    onChange={(e) => handleSwitchChange('midYearConvention', e.target.checked)}
                  />
                }
                label="Mid-Year Convention"
              />
              
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Check if cash flows occur mid-year (uncheck for year-end)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};

export default ValuationAssumptions; 