import React from 'react';
import { Box, Typography, CircularProgress, Paper } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

/**
 * Loading spinner component
 * Displays a loading animation with customizable message
 * 
 * @param {string} message - Loading message to display
 */
const LoadingSpinner = ({ message = "Running Analysis..." }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        p: 4,
      }}
    >
      <Paper
        sx={{
          p: 4,
          borderRadius: 3,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          textAlign: 'center',
          maxWidth: 400,
          width: '100%',
        }}
        className="card-hover"
      >
        {/* Loading Icon */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            mb: 3,
            mx: 'auto',
            position: 'relative',
          }}
        >
          <CircularProgress
            size={60}
            thickness={4}
            sx={{
              color: 'white',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              },
            }}
          />
          <TrendingUp
            sx={{
              position: 'absolute',
              color: 'white',
              fontSize: 24,
            }}
          />
        </Box>
        
        {/* Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: 'primary.main',
            mb: 2,
          }}
        >
          Processing Valuation
        </Typography>
        
        {/* Message */}
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mb: 3 }}
        >
          {message}
        </Typography>
        
        {/* Animated Dots */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            gap: 1,
          }}
        >
          {[0, 1, 2].map((i) => (
            <Box
              key={i}
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: 'primary.main',
                animation: 'pulse 1.5s ease-in-out infinite',
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </Box>
      </Paper>
      
      {/* Animation Styles */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              opacity: 0.4;
              transform: scale(1);
            }
            50% {
              opacity: 1;
              transform: scale(1.2);
            }
          }
        `}
      </style>
    </Box>
  );
};

export default LoadingSpinner; 