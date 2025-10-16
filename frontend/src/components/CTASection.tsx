'use client';

import React from 'react';
import { ArrowRight } from 'lucide-react';

interface CTASectionProps {
  onStartAnalysis?: () => void;
}

const CTASection: React.FC<CTASectionProps> = ({ onStartAnalysis }) => {
  return (
    <section className="pb-16">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center bg-gradient-to-r from-blue-500/20 to-purple-600/20 p-12 rounded-2xl border border-purple-400/30">
          <h3 className="text-3xl font-bold text-white mb-4">
            Ready to protect your business interests?
          </h3>
          <p className="text-purple-200 text-lg mb-6 max-w-2xl mx-auto">
            Join thousands of professionals who trust ContractCopilot for
            comprehensive contract analysis and risk assessment.
          </p>
          <button
            onClick={onStartAnalysis}
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-10 py-4 rounded-lg font-medium text-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
            type="button"
            aria-label="Start free contract analysis"
          >
            <span>Start Free Analysis</span>
            <ArrowRight className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
