import { Download, Upload } from 'lucide-react';
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

// Get API base URL from environment or use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

export function CSVUpload({ onDataLoaded }) {
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    fetch(`${API_BASE_URL}/valuation/csv/upload`, {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          onDataLoaded(data.data);
          setUploadStatus('✅ CSV uploaded successfully! Form fields have been updated.');
          // Clear status after 5 seconds
          setTimeout(() => setUploadStatus(''), 5000);
        } else {
          setUploadStatus('❌ Error: ' + (data.error || 'Upload failed'));
        }
      })
      .catch(error => {
        console.error('Error uploading CSV:', error);
        setUploadStatus('❌ Error: ' + error.message);
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
    // Create a temporary link element to trigger download
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}/valuation/csv/sample`;
    link.download = 'sample_input.csv';
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

      {/* Upload Status Message */}
      {uploadStatus && (
        <div className={`p-3 rounded-lg text-sm ${uploadStatus.includes('✅')
          ? 'bg-green-100 text-green-800 border border-green-200'
          : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
          {uploadStatus}
        </div>
      )}
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