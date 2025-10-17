'use client';

import React from 'react';

const HeaderSimple: React.FC = () => {
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
            <div className="flex items-center space-x-2 text-green-400">
              <div className="w-3 h-3 bg-green-400 rounded-full" />
              <span className="text-sm">Ready</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default HeaderSimple;
