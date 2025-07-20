import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box } from '@mui/material';

import Header from './components/Header';
import ValuationForm from './components/ValuationForm';
import Results from './components/Results';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1f77b4',
    },
    secondary: {
      main: '#ff7f0e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h1: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      textAlign: 'center',
      marginBottom: '0.5rem',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 'bold',
      marginBottom: '1rem',
    },
  },
});

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          <Header />
          <Container maxWidth="xl" sx={{ py: 4 }}>
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
                    onBack={() => {
                      setResults(null);
                      window.location.href = '/';
                    }}
                  />
                } 
              />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
