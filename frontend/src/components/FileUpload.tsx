'use client';

import React, { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '../constants/features';

interface FileUploadProps {
  onFileSelect?: (file: File) => void;
  className?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  className = '',
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (!SUPPORTED_FILE_TYPES.includes(file.type as any)) {
      return 'Please upload a PDF, DOC, or DOCX file.';
    }

    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 10MB.';
    }

    return null;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const validationError = validateFile(file);

      if (validationError) {
        setError(validationError);
        return;
      }

      setUploadedFile(file);
      onFileSelect?.(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);

    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validationError = validateFile(file);

      if (validationError) {
        setError(validationError);
        return;
      }

      setUploadedFile(file);
      onFileSelect?.(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setError(null);
  };

  return (
    <section className={`mb-12 ${className}`}>
      <div className="max-w-2xl mx-auto px-4">
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
            dragActive
              ? 'border-blue-400 bg-blue-400/10'
              : error
                ? 'border-red-400 bg-red-400/10'
                : 'border-purple-400/50 bg-black/20 hover:border-purple-400 hover:bg-black/30'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="contract-upload"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept=".pdf,.doc,.docx"
            onChange={handleFileSelect}
            aria-label="Upload contract file"
          />

          {!uploadedFile ? (
            <>
              <div className="bg-purple-500/20 p-6 rounded-full w-fit mx-auto mb-6">
                <Upload className="h-12 w-12 text-purple-400" />
              </div>
              <h3 className="text-2xl font-semibold text-white mb-3">
                Upload Your Contract
              </h3>
              <p className="text-purple-200 mb-6">
                Drag and drop your contract here, or{' '}
                <span className="text-blue-400 underline">browse files</span>
              </p>
              {error && (
                <p className="text-red-400 text-sm mb-4" role="alert">
                  {error}
                </p>
              )}
              <p className="text-purple-400/70 text-sm">
                Supports PDF, DOC, DOCX files up to 10MB
              </p>
            </>
          ) : (
            <div className="flex items-center justify-between bg-black/40 p-4 rounded-lg">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-green-400" />
                <div className="text-left">
                  <p className="text-white font-medium">{uploadedFile.name}</p>
                  <p className="text-purple-300 text-sm">
                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={handleRemoveFile}
                className="p-2 text-red-400 hover:text-red-300 transition-colors"
                aria-label="Remove file"
                type="button"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default FileUpload;
