import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box } from '@mui/material';

// Components
import Header from './components/Header';
import Footer from './components/Footer';
import ValuationForm from './components/ValuationForm';
import Results from './components/Results';

// Theme
import { theme } from './theme';

// Styles
import './App.css';

/**
 * Main application component
 * Handles routing and global state management
 */
function App() {
  // Global state for results and loading
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  /**
   * Handle navigation back to form
   * Clears results and redirects to home
   */
  const handleBackToForm = () => {
    setResults(null);
    window.location.href = '/';
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box 
          sx={{ 
            minHeight: '100vh', 
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Header />
          
          <Container maxWidth="xl" sx={{ py: { xs: 2, md: 4 }, flex: 1 }}>
            <Routes>
              <Route 
                path="/" 
                element={
                  <ValuationForm 
                    setResults={setResults} 
                    setLoading={setLoading}
                    loading={loading}
                  />
                } 
              />
              <Route 
                path="/results" 
                element={
                  <Results 
                    results={results} 
                    loading={loading}
                    onBack={handleBackToForm}
                  />
                } 
              />
            </Routes>
          </Container>
          
          <Footer />
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
