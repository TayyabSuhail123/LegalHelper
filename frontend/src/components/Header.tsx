'use client';

import React from 'react';
import { CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import { useHealthCheck } from '../hooks/useApi';

const Header: React.FC = () => {
  const { data: healthData, isLoading: healthLoading, error } = useHealthCheck();

  // Debug: Log the health check state
  React.useEffect(() => {
    console.log('Health check state:', { healthData, healthLoading, error });
    if (error) {
      console.error('Health check error details:', error);
    }
  }, [healthData, healthLoading, error]);

  return (
    <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              ContractCopilot
            </h1>
            <span className="text-purple-300 text-sm hidden sm:inline">
              AI-Powered Legal Document Risk Scanner
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {healthLoading ? (
              <div className="flex items-center space-x-2 text-yellow-400">
                <Clock className="h-4 w-4 animate-pulse" />
                <span className="text-sm">Checking status...</span>
              </div>
            ) : error ? (
              <div className="flex items-center space-x-2 text-red-400">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm">Backend Offline</span>
              </div>
            ) : healthData?.status === 'healthy' ? (
              <div className="flex items-center space-x-2 text-green-400">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm">System Online</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-gray-400">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm">Status Unknown</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
