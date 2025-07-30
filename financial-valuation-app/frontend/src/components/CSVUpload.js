import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Download } from 'lucide-react';

export function CSVUpload({ onDataLoaded }) {
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    const formData = new FormData();
    formData.append('file', file);
    fetch('/api/csv/upload', {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          onDataLoaded(data.data);
        }
      });
  }, [onDataLoaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false
  });

  const downloadSample = () => {
    window.open('/api/csv/sample', '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <button
          onClick={downloadSample}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Download size={16} />
          Download Sample CSV
        </button>
      </div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive ? 'Drop the CSV file here' : 'Drag & drop a CSV file, or click to select'}
        </p>
      </div>
    </div>
  );
} 