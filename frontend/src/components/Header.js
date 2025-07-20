import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import CalculateIcon from '@mui/icons-material/Calculate';

const Header = () => {
  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <CalculateIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            Financial Valuation Engine
          </Link>
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
            By Pranay Upreti
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 