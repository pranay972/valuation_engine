import React from 'react';

export const LoadingSkeleton = ({ className = '' }) => {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="skeleton h-4 rounded mb-2"></div>
      <div className="skeleton h-4 rounded mb-2 w-3/4"></div>
      <div className="skeleton h-4 rounded w-1/2"></div>
    </div>
  );
};

export const CardSkeleton = ({ className = '' }) => {
  return (
    <div className={`card ${className}`}>
      <div className="skeleton h-6 rounded mb-4 w-2/3"></div>
      <div className="skeleton h-4 rounded mb-2"></div>
      <div className="skeleton h-4 rounded mb-2 w-4/5"></div>
      <div className="skeleton h-4 rounded w-3/4"></div>
    </div>
  );
};

export const FormSkeleton = ({ className = '' }) => {
  return (
    <div className={`space-y-6 ${className}`}>
      <div className="space-y-2">
        <div className="skeleton h-4 rounded w-24"></div>
        <div className="skeleton h-12 rounded-lg"></div>
      </div>
      <div className="space-y-2">
        <div className="skeleton h-4 rounded w-32"></div>
        <div className="skeleton h-12 rounded-lg"></div>
      </div>
      <div className="space-y-2">
        <div className="skeleton h-4 rounded w-28"></div>
        <div className="skeleton h-12 rounded-lg"></div>
      </div>
    </div>
  );
};

export const TableSkeleton = ({ rows = 5, columns = 4, className = '' }) => {
  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="flex gap-4 mb-4">
        {Array.from({ length: columns }).map((_, index) => (
          <div key={index} className="skeleton h-6 rounded w-24"></div>
        ))}
      </div>
      
      {/* Rows */}
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="flex gap-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <div key={colIndex} className="skeleton h-4 rounded w-20"></div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export const ChartSkeleton = ({ className = '' }) => {
  return (
    <div className={`card-elevated ${className}`}>
      <div className="skeleton h-6 rounded mb-2 w-48"></div>
      <div className="skeleton h-4 rounded mb-6 w-64"></div>
      <div className="skeleton h-80 rounded-lg"></div>
    </div>
  );
};

export const AnalysisSelectionSkeleton = ({ className = '' }) => {
  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="text-center space-y-6 mb-12">
        <div className="skeleton h-16 w-16 rounded-full mx-auto"></div>
        <div className="skeleton h-10 rounded w-96 mx-auto"></div>
        <div className="skeleton h-6 rounded w-2xl mx-auto"></div>
      </div>
      
      {/* Grid */}
      <div className="grid-cards mb-12">
        {Array.from({ length: 6 }).map((_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
      
      {/* Summary */}
      <CardSkeleton className="text-center" />
    </div>
  );
};

export const ResultsSkeleton = ({ className = '' }) => {
  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="text-center space-y-6 mb-12">
        <div className="skeleton h-12 rounded w-80 mx-auto"></div>
        <div className="skeleton h-6 rounded w-96 mx-auto"></div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="card text-center">
            <div className="skeleton h-8 rounded w-32 mx-auto mb-2"></div>
            <div className="skeleton h-6 rounded w-24 mx-auto"></div>
          </div>
        ))}
      </div>
      
      {/* Charts */}
      <div className="space-y-8">
        <ChartSkeleton />
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  );
};

export const InputFormSkeleton = ({ className = '' }) => {
  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="text-center space-y-6 mb-12">
        <div className="skeleton h-12 rounded w-96 mx-auto"></div>
        <div className="skeleton h-6 rounded w-2xl mx-auto"></div>
      </div>
      
      {/* Form Sections */}
      <div className="space-y-8">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="card">
            <div className="skeleton h-6 rounded w-48 mb-6"></div>
            <FormSkeleton />
          </div>
        ))}
      </div>
      
      {/* Submit Button */}
      <div className="text-center mt-8">
        <div className="skeleton h-12 rounded w-48 mx-auto"></div>
      </div>
    </div>
  );
};

export const PageSkeleton = ({ type = 'default', className = '' }) => {
  switch (type) {
    case 'analysis-selection':
      return <AnalysisSelectionSkeleton className={className} />;
    case 'input-form':
      return <InputFormSkeleton className={className} />;
    case 'results':
      return <ResultsSkeleton className={className} />;
    default:
      return <LoadingSkeleton className={className} />;
  }
};
