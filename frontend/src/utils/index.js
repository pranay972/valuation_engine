/**
 * Utility functions for the application
 * Common operations and helper functions
 */

import { ERROR_MESSAGES } from '../constants';

/**
 * Format currency values
 * @param {number} value - The value to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value, currency = 'USD') => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * Format percentage values
 * @param {number} value - The value to format (as decimal)
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format number with commas
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 0)
 * @returns {string} Formatted number string
 */
export const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A';
  }
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate number range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} True if value is in range
 */
export const isInRange = (value, min, max) => {
  return value >= min && value <= max;
};

/**
 * Deep clone an object
 * @param {any} obj - Object to clone
 * @returns {any} Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item));
  }
  
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
};

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Parse CSV string to array of objects
 * @param {string} csv - CSV string
 * @returns {Array} Array of objects
 */
export const parseCSV = (csv) => {
  try {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        const values = lines[i].split(',');
        const row = {};
        headers.forEach((header, index) => {
          const value = values[index] ? values[index].trim() : '';
          // Convert numeric values to numbers, keep strings as strings
          if (header.includes('/') || !isNaN(value)) {
            row[header] = isNaN(value) ? value : parseFloat(value);
          } else {
            row[header] = value;
          }
        });
        data.push(row);
      }
    }
    
    return data;
  } catch (error) {
    console.error('Error parsing CSV:', error);
    throw new Error(ERROR_MESSAGES.FILE.UPLOAD_ERROR);
  }
};

/**
 * Download data as CSV file
 * @param {Array} data - Data to download
 * @param {string} filename - Filename for download
 */
export const downloadCSV = (data, filename) => {
  if (!data || data.length === 0) {
    console.warn('No data to download');
    return;
  }
  
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => row[header]).join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

/**
 * Calculate statistics from array of numbers
 * @param {Array} values - Array of numeric values
 * @returns {Object} Statistics object
 */
export const calculateStats = (values) => {
  if (!values || values.length === 0) {
    return {
      mean: 0,
      median: 0,
      min: 0,
      max: 0,
      count: 0,
    };
  }
  
  const sortedValues = values.sort((a, b) => a - b);
  const count = values.length;
  const mean = values.reduce((sum, val) => sum + val, 0) / count;
  const median = count % 2 === 0 
    ? (sortedValues[count / 2 - 1] + sortedValues[count / 2]) / 2
    : sortedValues[Math.floor(count / 2)];
  const min = sortedValues[0];
  const max = sortedValues[count - 1];
  
  return {
    mean,
    median,
    min,
    max,
    count,
  };
};

/**
 * Get percentile value from sorted array
 * @param {Array} sortedValues - Sorted array of values
 * @param {number} percentile - Percentile (0-100)
 * @returns {number} Percentile value
 */
export const getPercentile = (sortedValues, percentile) => {
  if (!sortedValues || sortedValues.length === 0) {
    return 0;
  }
  
  const index = Math.floor((percentile / 100) * (sortedValues.length - 1));
  return sortedValues[index];
}; 