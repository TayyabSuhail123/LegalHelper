'use client';

import React from 'react';

const HeroSection: React.FC = () => {
  return (
    <section className="text-center py-16 px-4">
      <h2 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-6 animate-fadeIn">
        Contract Analysis
        <br />
        <span className="text-white">Redefined</span>
      </h2>

      <p className="text-xl text-purple-200 max-w-3xl mx-auto mb-12 animate-slideUp leading-relaxed">
        Harness the power of AI to identify legal risks, analyze contract terms,
        and protect your business interests with unparalleled precision and
        speed.
      </p>

      <div className="flex flex-wrap justify-center gap-4 text-sm text-purple-300">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full" />
          <span>99.9% Accuracy</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full" />
          <span>Enterprise Security</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-purple-400 rounded-full" />
          <span>Instant Results</span>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
