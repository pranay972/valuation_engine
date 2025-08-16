import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Download, FileText, CheckCircle, AlertCircle } from 'lucide-react';

export function CSVUpload({ onDataLoaded }) {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus({ type: 'uploading', message: 'Processing file...' });

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/csv/upload', {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setUploadStatus({ type: 'success', message: 'File uploaded successfully!' });
          onDataLoaded(data.data);
          setTimeout(() => setUploadStatus(null), 3000);
        } else {
          setUploadStatus({ type: 'error', message: data.message || 'Upload failed' });
        }
      })
      .catch(error => {
        setUploadStatus({ type: 'error', message: 'Network error occurred' });
      })
      .finally(() => {
        setIsUploading(false);
      });
  }, [onDataLoaded]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB limit
  });

  const downloadSample = () => {
    window.open('/api/csv/sample', '_blank');
  };

  const getStatusIcon = () => {
    switch (uploadStatus?.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'uploading':
        return <div className="h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (uploadStatus?.type) {
      case 'success':
        return 'border-green-200 bg-green-50 text-green-800';
      case 'error':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'uploading':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Upload Financial Data
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Upload your CSV file containing financial data for valuation analysis
        </p>
      </div>

      {/* Download Sample */}
      <div className="flex justify-center">
        <button
          onClick={downloadSample}
          className="btn btn-outline"
        >
          <Download className="h-4 w-4" />
          Download Sample CSV
        </button>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
          isDragActive && !isDragReject
            ? 'border-blue-400 bg-blue-50'
            : isDragReject
            ? 'border-red-400 bg-red-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        
        <div className="flex justify-center mb-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
            isDragActive && !isDragReject
              ? 'bg-blue-100 text-blue-600'
              : 'bg-gray-100 text-gray-400'
          }`}>
            <Upload className="h-8 w-8" />
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-lg font-medium text-gray-900">
            {isDragActive && !isDragReject
              ? 'Drop your CSV file here'
              : isDragReject
              ? 'Invalid file type'
              : 'Drag & drop a CSV file, or click to select'
            }
          </p>
          <p className="text-sm text-gray-500">
            {isDragReject 
              ? 'Please upload a valid CSV file'
              : 'Supports CSV files up to 10MB'
            }
          </p>
        </div>

        <div className="mt-4 flex justify-center">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">
            <FileText className="h-3 w-3" />
            <span>CSV Format</span>
          </div>
        </div>
      </div>

      {/* Status Message */}
      {uploadStatus && (
        <div className={`flex items-center justify-center space-x-3 p-4 rounded-lg border ${getStatusColor()}`}>
          {getStatusIcon()}
          <span className="font-medium">{uploadStatus.message}</span>
        </div>
      )}

      {/* Guidelines */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h4 className="font-semibold text-gray-900 mb-4">Upload Guidelines</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-600">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Maximum file size: 10MB</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Supported format: CSV only</span>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Use comma-separated values</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Include header row</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 