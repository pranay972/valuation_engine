import { useState, useCallback } from 'react';
import { API_CONFIG, ERROR_MESSAGES } from '../constants';

/**
 * Custom hook for API calls
 * Provides loading state, error handling, and data management
 */
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Make API request with error handling
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @returns {Promise} API response
   */
  const apiCall = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const url = `${API_CONFIG.BASE_URL}${endpoint}`;
      const config = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: JSON.stringify(options.data),
        ...options,
      };

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      let errorMessage = ERROR_MESSAGES.API.SERVER_ERROR;

      if (err.name === 'AbortError') {
        errorMessage = ERROR_MESSAGES.API.TIMEOUT;
      } else if (err.message.includes('Failed to fetch')) {
        errorMessage = ERROR_MESSAGES.API.NETWORK_ERROR;
      } else if (err.message.includes('HTTP')) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Make valuation API call
   * @param {Object} formData - Form data to send
   * @returns {Promise} Valuation results
   */
  const runValuation = useCallback(async (formData) => {
    return apiCall(API_CONFIG.ENDPOINTS.VALUATION, {
      data: formData,
    });
  }, [apiCall]);

  /**
   * Check API health
   * @returns {Promise} Health status
   */
  const checkHealth = useCallback(async () => {
    return apiCall(API_CONFIG.ENDPOINTS.HEALTH, {
      method: 'GET',
    });
  }, [apiCall]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    apiCall,
    runValuation,
    checkHealth,
    clearError,
  };
}; 