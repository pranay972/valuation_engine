import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('Request config:', config);
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    console.log('Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data,
      headers: error.response?.headers
    });
    return Promise.reject(error);
  }
);

// Analysis API
export const analysisAPI = {
  getAnalysisTypes: () => api.get('/analysis/types'),
  getAnalyses: () => api.get('/analysis'),
  getAnalysis: (id) => api.get(`/analysis/${id}`),
  createAnalysis: (data) => api.post('/analysis', data),
  updateAnalysis: (id, data) => api.put(`/analysis/${id}`, data),
  deleteAnalysis: (id) => api.delete(`/analysis/${id}`),
};

// Valuation API
export const valuationAPI = {
  submitInputs: (analysisId, data) => api.post(`/valuation/${analysisId}/inputs`, data),
  getInputs: (analysisId) => api.get(`/valuation/${analysisId}/inputs`),
  validateInputs: (analysisId, data) => api.post(`/valuation/${analysisId}/validate`, data),
};

// Results API - Fixed endpoints to match backend
export const resultsAPI = {
  getResults: (analysisId) => api.get(`/results/${analysisId}/results`),
  getStatus: (analysisId) => api.get(`/results/${analysisId}/status`),
  getSummary: (analysisId) => api.get(`/results/${analysisId}/results/summary`),
  exportResults: (analysisId, format = 'json') =>
    api.get(`/results/${analysisId}/results/export?format=${format}`),
  deleteResults: (analysisId) => api.delete(`/results/${analysisId}/results`),
};

export default api; 