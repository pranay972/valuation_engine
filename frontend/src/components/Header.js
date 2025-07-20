import React from 'react';
import { AppBar, Toolbar, Typography, Box, Container, Chip } from '@mui/material';
import { Link } from 'react-router-dom';
import CalculateIcon from '@mui/icons-material/Calculate';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

/**
 * Application header component
 * Displays branding and navigation
 */
const Header = () => {
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ px: { xs: 0 } }}>
          {/* Logo and Brand */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: '12px',
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(10px)',
                mr: 2,
              }}
            >
              <CalculateIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            
            <Box>
              <Typography 
                variant="h6" 
                component={Link} 
                to="/" 
                sx={{ 
                  textDecoration: 'none', 
                  color: 'white',
                  fontWeight: 700,
                  letterSpacing: '-0.025em',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                Financial Valuation Engine
                <Chip
                  label="Pro"
                  size="small"
                  sx={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    fontSize: '0.7rem',
                    height: 20,
                    '& .MuiChip-label': {
                      px: 1,
                    },
                  }}
                />
              </Typography>
              
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.8)',
                  display: 'block',
                  mt: -0.5,
                }}
              >
                Advanced DCF & Valuation Analysis
              </Typography>
            </Box>
          </Box>
          
          {/* Author Info */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUpIcon 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.8)', 
                  fontSize: 20 
                }} 
              />
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.9)',
                  fontWeight: 500,
                }}
              >
                By Pranay Upreti
              </Typography>
            </Box>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 