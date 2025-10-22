'use client';

import React from 'react';
import { FileText, File } from 'lucide-react';

interface DocumentViewerProps {
  file: File;
  className?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ file, className = '' }) => {
  const getFileIcon = () => {
    switch (file.type) {
      case 'application/pdf':
        return <FileText className="h-16 w-16 text-red-400" />;
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return <FileText className="h-16 w-16 text-blue-400" />;
      case 'application/msword':
        return <FileText className="h-16 w-16 text-blue-400" />;
      case 'text/plain':
        return <File className="h-16 w-16 text-gray-400" />;
      default:
        return <File className="h-16 w-16 text-purple-400" />;
    }
  };

  const getFileTypeName = () => {
    switch (file.type) {
      case 'application/pdf':
        return 'PDF Document';
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'Microsoft Word Document';
      case 'application/msword':
        return 'Microsoft Word Document (Legacy)';
      case 'text/plain':
        return 'Text Document';
      default:
        return 'Document';
    }
  };

  return (
    <div className={`bg-gray-900 rounded-lg p-8 text-center ${className}`}>
      <div className="flex flex-col items-center space-y-4">
        {getFileIcon()}
        <div>
          <h3 className="text-lg font-semibold text-white">{file.name}</h3>
          <p className="text-gray-400 text-sm">{getFileTypeName()}</p>
          <p className="text-gray-500 text-xs mt-1">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 w-full max-w-md">
          <p className="text-gray-300 text-sm">
            {file.type === 'application/pdf' 
              ? '📄 PDF documents will show a preview once PDF viewer is properly configured'
              : '📋 Document preview not available for this file type'
            }
          </p>
          <p className="text-gray-400 text-xs mt-2">
            Click &quot;Analyze Legal Document&quot; to extract and analyze the content.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
