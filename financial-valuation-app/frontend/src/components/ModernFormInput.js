import React, { useState } from 'react';
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';

export const ModernFormInput = ({
  label,
  type = 'text',
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  success,
  disabled = false,
  required = false,
  className = '',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [hasValue, setHasValue] = useState(!!value);

  const handleChange = (e) => {
    setHasValue(!!e.target.value);
    onChange?.(e);
  };

  const handleFocus = () => setIsFocused(true);
  const handleBlur = (e) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const inputType = type === 'password' && showPassword ? 'text' : type;

  const getInputClasses = () => {
    let baseClasses = 'form-input w-full transition-all duration-200';
    
    if (error) {
      baseClasses += ' form-input-error';
    } else if (success) {
      baseClasses += ' form-input-success';
    } else if (isFocused) {
      baseClasses += ' border-primary-300 shadow-sm shadow-primary-500/25';
    }
    
    if (disabled) {
      baseClasses += ' opacity-50 cursor-not-allowed';
    }
    
    return baseClasses;
  };

  const getLabelClasses = () => {
    let baseClasses = 'absolute left-4 transition-all duration-200 pointer-events-none';
    
    if (isFocused || hasValue) {
      baseClasses += ' -top-2.5 left-3 text-xs font-medium bg-white px-2';
      if (error) {
        baseClasses += ' text-error-600';
      } else if (success) {
        baseClasses += ' text-accent-600';
      } else {
        baseClasses += ' text-primary-600';
      }
    } else {
      baseClasses += ' top-4 text-neutral-500';
    }
    
    return baseClasses;
  };

  return (
    <div className={`relative ${className}`}>
      {/* Input Field */}
      <div className="relative">
        <input
          type={inputType}
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={isFocused ? placeholder : ''}
          disabled={disabled}
          required={required}
          className={getInputClasses()}
          {...props}
        />
        
        {/* Floating Label */}
        <label className={getLabelClasses()}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
        
        {/* Password Toggle */}
        {type === 'password' && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 p-1 text-neutral-400 hover:text-neutral-600 transition-colors duration-200"
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        )}
        
        {/* Status Icons */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          {error && <AlertCircle className="h-4 w-4 text-error-500" />}
          {success && !error && <CheckCircle className="h-4 w-4 text-accent-500" />}
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-error-600">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      {/* Success Message */}
      {success && !error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-accent-600">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}
    </div>
  );
};

export const ModernFormSelect = ({
  label,
  value,
  onChange,
  onBlur,
  options = [],
  error,
  success,
  disabled = false,
  required = false,
  className = '',
  placeholder = 'Select an option',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(!!value);

  const handleChange = (e) => {
    setHasValue(!!e.target.value);
    onChange?.(e);
  };

  const handleFocus = () => setIsFocused(true);
  const handleBlur = (e) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const getSelectClasses = () => {
    let baseClasses = 'form-select w-full transition-all duration-200';
    
    if (error) {
      baseClasses += ' form-input-error';
    } else if (success) {
      baseClasses += ' form-input-success';
    } else if (isFocused) {
      baseClasses += ' border-primary-300 shadow-sm shadow-primary-500/25';
    }
    
    if (disabled) {
      baseClasses += ' opacity-50 cursor-not-allowed';
    }
    
    return baseClasses;
  };

  const getLabelClasses = () => {
    let baseClasses = 'absolute left-4 transition-all duration-200 pointer-events-none';
    
    if (isFocused || hasValue) {
      baseClasses += ' -top-2.5 left-3 text-xs font-medium bg-white px-2';
      if (error) {
        baseClasses += ' text-error-600';
      } else if (success) {
        baseClasses += ' text-accent-600';
      } else {
        baseClasses += ' text-primary-600';
      }
    } else {
      baseClasses += ' top-4 text-neutral-500';
    }
    
    return baseClasses;
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <select
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={disabled}
          required={required}
          className={getSelectClasses()}
          {...props}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        
        <label className={getLabelClasses()}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
        
        {/* Status Icons */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2">
          {error && <AlertCircle className="h-4 w-4 text-error-500" />}
          {success && !error && <CheckCircle className="h-4 w-4 text-accent-500" />}
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-error-600">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      {/* Success Message */}
      {success && !error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-accent-600">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}
    </div>
  );
};

export const ModernFormTextarea = ({
  label,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  success,
  disabled = false,
  required = false,
  className = '',
  rows = 4,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(!!value);

  const handleChange = (e) => {
    setHasValue(!!e.target.value);
    onChange?.(e);
  };

  const handleFocus = () => setIsFocused(true);
  const handleBlur = (e) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const getTextareaClasses = () => {
    let baseClasses = 'form-textarea w-full transition-all duration-200';
    
    if (error) {
      baseClasses += ' form-input-error';
    } else if (success) {
      baseClasses += ' form-input-success';
    } else if (isFocused) {
      baseClasses += ' border-primary-300 shadow-sm shadow-primary-500/25';
    }
    
    if (disabled) {
      baseClasses += ' opacity-50 cursor-not-allowed';
    }
    
    return baseClasses;
  };

  const getLabelClasses = () => {
    let baseClasses = 'absolute left-4 transition-all duration-200 pointer-events-none';
    
    if (isFocused || hasValue) {
      baseClasses += ' -top-2.5 left-3 text-xs font-medium bg-white px-2';
      if (error) {
        baseClasses += ' text-error-600';
      } else if (success) {
        baseClasses += ' text-accent-600';
      } else {
        baseClasses += ' text-primary-600';
      }
    } else {
      baseClasses += ' top-4 text-neutral-500';
    }
    
    return baseClasses;
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <textarea
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={isFocused ? placeholder : ''}
          disabled={disabled}
          required={required}
          rows={rows}
          className={getTextareaClasses()}
          {...props}
        />
        
        <label className={getLabelClasses()}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
        
        {/* Status Icons */}
        <div className="absolute right-4 top-4">
          {error && <AlertCircle className="h-4 w-4 text-error-500" />}
          {success && !error && <CheckCircle className="h-4 w-4 text-accent-500" />}
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-error-600">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      {/* Success Message */}
      {success && !error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-accent-600">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}
    </div>
  );
};

export const ModernFormCheckbox = ({
  label,
  checked,
  onChange,
  error,
  disabled = false,
  required = false,
  className = '',
  ...props
}) => {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <div className="flex items-center h-5">
        <input
          type="checkbox"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          required={required}
          className={`form-checkbox ${error ? 'border-error-300' : ''}`}
          {...props}
        />
      </div>
      <div className="flex-1">
        <label className="text-sm font-medium text-neutral-700 cursor-pointer">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
        {error && (
          <div className="mt-1 flex items-center gap-2 text-sm text-error-600">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};
