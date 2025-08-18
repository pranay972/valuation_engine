import { Download, Upload } from 'lucide-react';
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

// Backend API URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

export function CSVUpload({ onDataLoaded }) {
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    fetch(`${API_BASE_URL}/csv/upload`, {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          onDataLoaded(data.data);
        }
      })
      .catch(error => {
        console.error('Error uploading CSV:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [onDataLoaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
    disabled: loading
  });

  const downloadSample = () => {
    window.open(`${API_BASE_URL}/csv/sample`, '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <button
          onClick={downloadSample}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          disabled={loading}
        >
          <Download size={16} />
          Download Sample CSV
        </button>
      </div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        {loading ? (
          <>
            <div className="spinner mx-auto h-12 w-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
            <p className="mt-2 text-sm text-gray-600">Processing CSV file...</p>
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
              .animate-spin {
                animation: spin 1s linear infinite;
              }
            `}</style>
          </>
        ) : (
          <>
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-600">
              {isDragActive ? 'Drop the CSV file here' : 'Drag & drop a CSV file, or click to select'}
            </p>
          </>
        )}
      </div>
    </div>
  );
} 