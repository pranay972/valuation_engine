/**
 * Application constants
 * Centralized configuration for the entire application
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    VALUATION: '/api/valuation',
    HEALTH: '/health',
  },
  TIMEOUT: 30000, // 30 seconds
};

// Form Configuration
export const FORM_CONFIG = {
  DEFAULT_VALUES: {
    // Analysis Selection
    analyses: ['WACC DCF'],

    // Financial Projections
    inputMode: 'driver',
    revenue: [],
    ebitMargin: 0.20,
    capex: [],
    depreciation: [],
    nwcChanges: [],
    fcfSeries: [],
    shareCount: 100000000,
    costOfDebt: 0.05,
    currentDebt: 0,
    debtSchedule: {},

    // Valuation Assumptions
    wacc: 0.12,
    terminalGrowth: 0.025,
    taxRate: 0.25,
    midYearConvention: true,

    // Advanced Analysis
    mcRuns: 2000,
    variableSpecs: {
      wacc: {
        dist: 'normal',
        params: { loc: 0.12, scale: 0.01 }
      },
      terminal_growth: {
        dist: 'uniform',
        params: { low: 0.015, high: 0.025 }
      }
    },
    sensitivityRanges: {},
    scenarios: {},
    compsData: null,
  },

  VALIDATION: {
    MIN_MC_RUNS: 100,
    MAX_MC_RUNS: 10000,
    MIN_SENSITIVITY_STEPS: 2,
    MAX_SENSITIVITY_STEPS: 20,
  },
};

// Analysis Types
export const ANALYSIS_TYPES = {
  WACC_DCF: 'WACC DCF',
  APV_DCF: 'APV DCF',
  MONTE_CARLO: 'Monte Carlo',
  MULTIPLES: 'Multiples',
  SCENARIOS: 'Scenarios',
  SENSITIVITY: 'Sensitivity',
};

// UI Configuration
export const UI_CONFIG = {
  ANIMATIONS: {
    TRANSITION_DURATION: 300,
    HOVER_TRANSFORM: 'translateY(-2px)',
  },

  SPACING: {
    CARD_PADDING: 4,
    SECTION_MARGIN: 4,
    GRID_SPACING: 3,
  },

  COLORS: {
    SUCCESS: '#10b981',
    WARNING: '#f59e0b',
    ERROR: '#ef4444',
    INFO: '#3b82f6',
  },
};

// File Configuration
export const FILE_CONFIG = {
  ACCEPTED_TYPES: {
    CSV: '.csv',
  },
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
};

// Error Messages
export const ERROR_MESSAGES = {
  API: {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    TIMEOUT: 'Request timed out. Please try again.',
    SERVER_ERROR: 'Server error. Please try again later.',
    VALIDATION_ERROR: 'Invalid data provided.',
  },

  FORM: {
    REQUIRED_FIELD: 'This field is required.',
    INVALID_NUMBER: 'Please enter a valid number.',
    INVALID_PERCENTAGE: 'Please enter a valid percentage (0-100).',
    INVALID_RANGE: 'Minimum must be less than maximum.',
    INVALID_STEPS: 'Steps must be between 2 and 20.',
  },

  FILE: {
    INVALID_TYPE: 'Please select a valid CSV file.',
    TOO_LARGE: 'File size must be less than 5MB.',
    UPLOAD_ERROR: 'Error uploading file. Please try again.',
  },
};

// Success Messages
export const SUCCESS_MESSAGES = {
  FILE_UPLOADED: 'File uploaded successfully.',
  ANALYSIS_COMPLETE: 'Analysis completed successfully.',
  DATA_SAVED: 'Data saved successfully.',
}; 