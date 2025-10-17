'use client';

import React, { useState } from 'react';
import { Upload, FileText, X, Eye, Loader, AlertCircle, CheckCircle2 } from 'lucide-react';
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '../constants/features';
import DocumentViewer from './DocumentViewer';
import { apiService, type FileDetails } from '../api/apiService';

interface FileUploadProps {
  onFileSelect?: (file: File) => void;
  className?: string;
}

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  className = '',
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [fileDetails, setFileDetails] = useState<FileDetails | null>(null);
  const [showViewer, setShowViewer] = useState(false);
  const [extractedText, setExtractedText] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (!SUPPORTED_FILE_TYPES.includes(file.type as any)) {
      return 'Please upload a PDF, DOC, or DOCX file.';
    }

    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 50MB.';
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
      setShowViewer(true);
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
      setShowViewer(true);
      onFileSelect?.(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setError(null);
    setUploadStatus('idle');
    setFileDetails(null);
    setShowViewer(false);
    setExtractedText(null);
  };

  const handleAnalyzeDocument = async () => {
    if (!uploadedFile) return;

    try {
      setUploadStatus('uploading');
      setError(null);

      // Upload file to backend
      const uploadResponse = await apiService.uploadFile(uploadedFile);
      
      setUploadStatus('processing');

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const status = await apiService.getProcessingStatus(uploadResponse.file_id);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setUploadStatus('completed');
            
            // Get file details with extracted text
            const details = await apiService.getFileDetails(uploadResponse.file_id);
            setFileDetails(details);
            setExtractedText(details.extracted_text || null);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setUploadStatus('error');
            setError(status.error_message || 'Processing failed');
          }
        } catch (pollError) {
          clearInterval(pollInterval);
          setUploadStatus('error');
          setError('Failed to check processing status');
        }
      }, 1000);

    } catch (uploadError) {
      setUploadStatus('error');
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed');
    }
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
      case 'processing':
        return <Loader className="h-5 w-5 animate-spin text-blue-400" />;
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case 'uploading':
        return 'Uploading file...';
      case 'processing':
        return 'Extracting text from document...';
      case 'completed':
        return 'Analysis completed!';
      case 'error':
        return 'Analysis failed';
      default:
        return '';
    }
  };

  return (
    <section className={`mb-12 ${className}`}>
      <div className="max-w-4xl mx-auto px-4">
        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 mb-6 ${
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
                Upload Your Legal Document
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
                Supports PDF, DOC, DOCX files up to 50MB
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
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowViewer(!showViewer)}
                  className="p-2 text-blue-400 hover:text-blue-300 transition-colors"
                  aria-label="Toggle document viewer"
                  type="button"
                >
                  <Eye className="h-5 w-5" />
                </button>
                <button
                  onClick={handleRemoveFile}
                  className="p-2 text-red-400 hover:text-red-300 transition-colors"
                  aria-label="Remove file"
                  type="button"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Document Viewer */}
        {uploadedFile && showViewer && (
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-white mb-3">Document Preview</h4>
            <DocumentViewer file={uploadedFile} />
          </div>
        )}

        {/* Analysis Section */}
        {uploadedFile && (
          <div className="bg-black/40 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-white">Document Analysis</h4>
              {getStatusIcon() && (
                <div className="flex items-center space-x-2">
                  {getStatusIcon()}
                  <span className="text-sm text-gray-300">{getStatusText()}</span>
                </div>
              )}
            </div>

            {uploadStatus === 'idle' && (
              <div className="text-center">
                <p className="text-purple-200 mb-4">
                  Ready to analyze your legal document for potential risks and important clauses.
                </p>
                <button
                  onClick={handleAnalyzeDocument}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105"
                >
                  Analyze Legal Document
                </button>
              </div>
            )}

            {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
              <div className="text-center">
                <div className="animate-pulse text-purple-200 mb-2">
                  Processing your document...
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full animate-pulse" style={{ width: uploadStatus === 'uploading' ? '30%' : '70%' }}></div>
                </div>
              </div>
            )}

            {uploadStatus === 'completed' && extractedText && (
              <div>
                <h5 className="text-md font-medium text-white mb-3">Extracted Text:</h5>
                <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-gray-300 text-sm whitespace-pre-wrap">{extractedText}</pre>
                </div>
                <div className="mt-4 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
                  <p className="text-green-300 text-sm">
                    ✅ Text extraction completed successfully! 
                    {fileDetails && (
                      <span className="block mt-1">
                        File ID: {fileDetails.file_id} • 
                        Type: {fileDetails.file_type.toUpperCase()} • 
                        Size: {(fileDetails.file_size / 1024).toFixed(1)} KB
                      </span>
                    )}
                  </p>
                </div>
              </div>
            )}

            {uploadStatus === 'error' && error && (
              <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
                <p className="text-red-300 text-sm">❌ {error}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
};

export default FileUpload;
