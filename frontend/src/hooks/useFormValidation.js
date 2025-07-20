import { useState, useCallback } from 'react';
import { ERROR_MESSAGES, FORM_CONFIG } from '../constants';
import { isInRange } from '../utils';

/**
 * Custom hook for form validation
 * Provides validation state and validation functions
 */
export const useFormValidation = () => {
  const [errors, setErrors] = useState({});

  /**
   * Clear all errors
   */
  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  /**
   * Clear specific field error
   * @param {string} field - Field name
   */
  const clearFieldError = useCallback((field) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  }, []);

  /**
   * Set field error
   * @param {string} field - Field name
   * @param {string} message - Error message
   */
  const setFieldError = useCallback((field, message) => {
    setErrors(prev => ({
      ...prev,
      [field]: message,
    }));
  }, []);

  /**
   * Validate required field
   * @param {string} field - Field name
   * @param {any} value - Field value
   * @returns {boolean} True if valid
   */
  const validateRequired = useCallback((field, value) => {
    if (!value || (typeof value === 'string' && value.trim() === '') || 
        (Array.isArray(value) && value.length === 0)) {
      setFieldError(field, ERROR_MESSAGES.FORM.REQUIRED_FIELD);
      return false;
    }
    clearFieldError(field);
    return true;
  }, [setFieldError, clearFieldError]);

  /**
   * Validate number field
   * @param {string} field - Field name
   * @param {any} value - Field value
   * @param {Object} options - Validation options
   * @returns {boolean} True if valid
   */
  const validateNumber = useCallback((field, value, options = {}) => {
    const { min, max, required = true } = options;

    if (required && !validateRequired(field, value)) {
      return false;
    }

    if (value === '' || value === null || value === undefined) {
      return true; // Allow empty if not required
    }

    const numValue = parseFloat(value);
    if (isNaN(numValue)) {
      setFieldError(field, ERROR_MESSAGES.FORM.INVALID_NUMBER);
      return false;
    }

    if (min !== undefined && numValue < min) {
      setFieldError(field, `Value must be at least ${min}`);
      return false;
    }

    if (max !== undefined && numValue > max) {
      setFieldError(field, `Value must be at most ${max}`);
      return false;
    }

    clearFieldError(field);
    return true;
  }, [validateRequired, setFieldError, clearFieldError]);

  /**
   * Validate percentage field
   * @param {string} field - Field name
   * @param {any} value - Field value
   * @returns {boolean} True if valid
   */
  const validatePercentage = useCallback((field, value) => {
    return validateNumber(field, value, { min: 0, max: 1 });
  }, [validateNumber]);

  /**
   * Validate Monte Carlo runs
   * @param {string} field - Field name
   * @param {any} value - Field value
   * @returns {boolean} True if valid
   */
  const validateMonteCarloRuns = useCallback((field, value) => {
    return validateNumber(field, value, {
      min: FORM_CONFIG.VALIDATION.MIN_MC_RUNS,
      max: FORM_CONFIG.VALIDATION.MAX_MC_RUNS,
    });
  }, [validateNumber]);

  /**
   * Validate sensitivity steps
   * @param {string} field - Field name
   * @param {any} value - Field value
   * @returns {boolean} True if valid
   */
  const validateSensitivitySteps = useCallback((field, value) => {
    return validateNumber(field, value, {
      min: FORM_CONFIG.VALIDATION.MIN_SENSITIVITY_STEPS,
      max: FORM_CONFIG.VALIDATION.MAX_SENSITIVITY_STEPS,
    });
  }, [validateNumber]);

  /**
   * Validate range (min < max)
   * @param {string} field - Field name
   * @param {number} min - Minimum value
   * @param {number} max - Maximum value
   * @returns {boolean} True if valid
   */
  const validateRange = useCallback((field, min, max) => {
    if (min >= max) {
      setFieldError(field, ERROR_MESSAGES.FORM.INVALID_RANGE);
      return false;
    }
    clearFieldError(field);
    return true;
  }, [setFieldError, clearFieldError]);

  /**
   * Validate series data
   * @param {string} field - Field name
   * @param {string} value - Series string
   * @returns {boolean} True if valid
   */
  const validateSeries = useCallback((field, value) => {
    if (!value || value.trim() === '') {
      return true; // Allow empty series
    }

    try {
      const numbers = value.split(',').map(x => {
        const trimmed = x.trim();
        if (!trimmed) return null;
        const parsed = parseFloat(trimmed);
        if (isNaN(parsed)) {
          throw new Error(`Invalid number: ${trimmed}`);
        }
        return parsed;
      }).filter(x => x !== null);

      if (numbers.length === 0) {
        setFieldError(field, 'Please enter at least one valid number');
        return false;
      }

      clearFieldError(field);
      return true;
    } catch (error) {
      setFieldError(field, error.message);
      return false;
    }
  }, [setFieldError, clearFieldError]);

  /**
   * Check if form has any errors
   * @returns {boolean} True if form has errors
   */
  const hasErrors = useCallback(() => {
    return Object.keys(errors).length > 0;
  }, [errors]);

  /**
   * Get error count
   * @returns {number} Number of errors
   */
  const getErrorCount = useCallback(() => {
    return Object.keys(errors).length;
  }, [errors]);

  return {
    errors,
    clearErrors,
    clearFieldError,
    setFieldError,
    validateRequired,
    validateNumber,
    validatePercentage,
    validateMonteCarloRuns,
    validateSensitivitySteps,
    validateRange,
    validateSeries,
    hasErrors,
    getErrorCount,
  };
}; 