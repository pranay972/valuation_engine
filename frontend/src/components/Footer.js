import React from 'react';
import { Box, Typography, Container, Link, Divider } from '@mui/material';
import { GitHub, LinkedIn, Email } from '@mui/icons-material';

/**
 * Application footer component
 * Displays branding, links, and copyright information
 */
const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        mt: 'auto',
        py: 4,
        background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
        color: 'white',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Container maxWidth="xl">
        {/* Main Footer Content */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', md: 'flex-start' },
            gap: 3,
          }}
        >
          {/* Brand Section */}
          <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                mb: 1,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Financial Valuation Engine
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                maxWidth: 300,
              }}
            >
              Advanced DCF analysis with Monte Carlo simulations, sensitivity analysis, 
              and scenario modeling for comprehensive financial valuations.
            </Typography>
          </Box>

          {/* Author Section */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: 1,
              alignItems: { xs: 'center', md: 'flex-end' },
            }}
          >
            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 500,
              }}
            >
              By Pranay Upreti
            </Typography>
            
            {/* Social Links */}
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                mt: 1,
              }}
            >
              <Link
                href="https://github.com/pranayupreti"
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&:hover': {
                    color: 'white',
                  },
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }}
              >
                <GitHub sx={{ fontSize: 20 }} />
                <Typography variant="body2">GitHub</Typography>
              </Link>
              
              <Link
                href="https://linkedin.com/in/pranayupreti"
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&:hover': {
                    color: 'white',
                  },
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }}
              >
                <LinkedIn sx={{ fontSize: 20 }} />
                <Typography variant="body2">LinkedIn</Typography>
              </Link>
              
              <Link
                href="mailto:pranay@example.com"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&:hover': {
                    color: 'white',
                  },
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }}
              >
                <Email sx={{ fontSize: 20 }} />
                <Typography variant="body2">Email</Typography>
              </Link>
            </Box>
          </Box>
        </Box>

        {/* Divider */}
        <Divider
          sx={{
            my: 3,
            borderColor: 'rgba(255, 255, 255, 0.1)',
          }}
        />

        {/* Bottom Section */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', sm: 'flex-start' },
            gap: 2,
          }}
        >
          {/* Copyright */}
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255, 255, 255, 0.5)',
              textAlign: { xs: 'center', sm: 'left' },
            }}
          >
            © 2024 Financial Valuation Engine. All rights reserved.
          </Typography>
          
          {/* Legal Links */}
          <Box
            sx={{
              display: 'flex',
              gap: 3,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            <Link
              href="#"
              sx={{
                color: 'rgba(255, 255, 255, 0.5)',
                textDecoration: 'none',
                '&:hover': {
                  color: 'white',
                },
                fontSize: '0.875rem',
              }}
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              sx={{
                color: 'rgba(255, 255, 255, 0.5)',
                textDecoration: 'none',
                '&:hover': {
                  color: 'white',
                },
                fontSize: '0.875rem',
              }}
            >
              Terms of Service
            </Link>
            <Link
              href="#"
              sx={{
                color: 'rgba(255, 255, 255, 0.5)',
                textDecoration: 'none',
                '&:hover': {
                  color: 'white',
                },
                fontSize: '0.875rem',
              }}
            >
              Documentation
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer; 