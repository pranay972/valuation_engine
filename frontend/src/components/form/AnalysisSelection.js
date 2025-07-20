import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  FormControlLabel,
  Checkbox,
  Grid,
  Alert,
  Box,
  Chip,
  Container,
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  CompareArrows,
  Timeline,
  Psychology,
  Tune,
} from '@mui/icons-material';

const AnalysisSelection = ({ analyses, onUpdate }) => {
  const analysisOptions = [
    { 
      key: 'WACC DCF', 
      label: 'WACC DCF', 
      description: 'Standard DCF using Weighted Average Cost of Capital',
      icon: TrendingUp,
      color: '#2563eb',
      popular: true,
    },
    { 
      key: 'APV DCF', 
      label: 'APV DCF', 
      description: 'Adjusted Present Value method for complex capital structures',
      icon: Analytics,
      color: '#10b981',
    },
    { 
      key: 'Monte Carlo', 
      label: 'Monte Carlo', 
      description: 'Uncertainty analysis with probability distributions',
      icon: Psychology,
      color: '#8b5cf6',
    },
    { 
      key: 'Multiples', 
      label: 'Comparable Multiples', 
      description: 'Peer company analysis using valuation multiples',
      icon: CompareArrows,
      color: '#f59e0b',
    },
    { 
      key: 'Scenarios', 
      label: 'Scenario Analysis', 
      description: 'What-if scenarios for different business outcomes',
      icon: Timeline,
      color: '#ef4444',
    },
    { 
      key: 'Sensitivity', 
      label: 'Sensitivity Analysis', 
      description: 'Parameter sensitivity testing',
      icon: Tune,
      color: '#06b6d4',
    },
  ];

  const handleChange = (analysisKey) => {
    const newAnalyses = analyses.includes(analysisKey)
      ? analyses.filter(a => a !== analysisKey)
      : [...analyses, analysisKey];
    onUpdate(newAnalyses);
  };

  return (
    <Container maxWidth="lg" className="slide-in">
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
          Select Analysis Types
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
          Choose the valuation methods you'd like to include in your analysis. 
          You can select multiple options for comprehensive results.
        </Typography>
      </Box>
      
      {analyses.length === 0 && (
        <Alert 
          severity="warning" 
          sx={{ 
            mb: 4,
            borderRadius: 3,
            fontSize: '1rem',
            '& .MuiAlert-icon': {
              color: 'warning.main',
              fontSize: '1.5rem',
            },
          }}
        >
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Please select at least one analysis type to proceed with the valuation.
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3}>
        {analysisOptions.map((option) => {
          const IconComponent = option.icon;
          const isSelected = analyses.includes(option.key);
          
          return (
            <Grid item xs={12} sm={6} md={4} key={option.key}>
              <Card 
                variant="outlined" 
                sx={{ 
                  cursor: 'pointer',
                  borderColor: isSelected ? option.color : 'grey.300',
                  borderWidth: isSelected ? 3 : 2,
                  background: isSelected 
                    ? `linear-gradient(135deg, ${option.color}08 0%, ${option.color}12 100%)`
                    : 'white',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': { 
                    borderColor: option.color,
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.12)',
                  },
                  position: 'relative',
                  overflow: 'hidden',
                  height: 200,
                  display: 'flex',
                  flexDirection: 'column',
                }}
                onClick={() => handleChange(option.key)}
                className="card-hover"
              >
                {option.popular && (
                  <Chip
                    label="Most Popular"
                    size="small"
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                      color: 'white',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      zIndex: 1,
                      boxShadow: '0 2px 8px rgba(245, 158, 11, 0.3)',
                    }}
                  />
                )}
                <CardContent sx={{ 
                  p: 3, 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  flex: 1,
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 1, flex: 1 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 48,
                        height: 48,
                        borderRadius: '12px',
                        background: isSelected 
                          ? `linear-gradient(135deg, ${option.color} 0%, ${option.color}dd 100%)`
                          : `${option.color}15`,
                        color: isSelected ? 'white' : option.color,
                        flexShrink: 0,
                        boxShadow: isSelected 
                          ? `0 6px 16px ${option.color}40`
                          : '0 3px 8px rgba(0, 0, 0, 0.1)',
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <IconComponent sx={{ fontSize: 24 }} />
                    </Box>
                    <Box sx={{ flex: 1, pt: 0.5, display: 'flex', flexDirection: 'column', height: '100%' }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={isSelected}
                            onChange={() => handleChange(option.key)}
                            sx={{
                              color: option.color,
                              '&.Mui-checked': {
                                color: option.color,
                              },
                              '& .MuiSvgIcon-root': {
                                fontSize: 24,
                              },
                            }}
                          />
                        }
                        label={
                          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                            <Typography 
                              variant="h6" 
                              sx={{ 
                                fontWeight: 600,
                                color: isSelected ? option.color : 'text.primary',
                                mb: 1,
                                fontSize: { xs: '1.1rem', md: '1.2rem' },
                              }}
                            >
                              {option.label}
                            </Typography>
                            <Typography 
                              variant="body2" 
                              color="text.secondary"
                              sx={{ 
                                lineHeight: 1.4,
                                fontSize: '0.875rem',
                                fontWeight: 400,
                                flex: 1,
                              }}
                            >
                              {option.description}
                            </Typography>
                          </Box>
                        }
                        sx={{ 
                          margin: 0,
                          width: '100%',
                          alignItems: 'flex-start',
                          height: '100%',
                        }}
                      />
                    </Box>
                  </Box>
                  
                  {/* Selection indicator */}
                  <Box sx={{ mt: 'auto', pt: 1 }}>
                    <Box
                      sx={{
                        height: 3,
                        borderRadius: 1.5,
                        background: isSelected 
                          ? `linear-gradient(90deg, ${option.color} 0%, ${option.color}dd 100%)`
                          : 'grey.200',
                        transition: 'all 0.3s ease',
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      
      {analyses.length > 0 && (
        <Box sx={{ mt: 6, textAlign: 'center' }}>
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              gap: 2,
              fontWeight: 600,
            }}
          >
            <Box 
              sx={{ 
                width: 12, 
                height: 12, 
                borderRadius: '50%', 
                backgroundColor: 'success.main',
                boxShadow: '0 2px 8px rgba(34, 197, 94, 0.3)',
              }} 
            />
            {analyses.length} analysis type{analyses.length > 1 ? 's' : ''} selected
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default AnalysisSelection; 