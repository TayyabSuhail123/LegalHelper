'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from '../src/components/Header';
import HeroSection from '../src/components/HeroSection';
import FileUpload from '../src/components/FileUpload';
import FeaturesGrid from '../src/components/FeaturesGrid';
import CTASection from '../src/components/CTASection';
import AnalysisResults from '../src/components/AnalysisResults';
import { AnalysisResult } from '../src/api/apiService';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

type AppView = 'upload' | 'results';

export default function Home() {
  const [currentView, setCurrentView] = useState<AppView>('upload');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleAnalysisComplete = (result: AnalysisResult) => {
    console.log('App: handleAnalysisComplete called with result:', result);
    setAnalysisResult(result);
    setCurrentView('results');
    console.log('App: Navigation to results view triggered');
  };

  const handleBackToUpload = () => {
    setCurrentView('upload');
    setAnalysisResult(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      {currentView === 'upload' && (
        <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <Header />
          <main>
            <HeroSection />
            <FileUpload onAnalysisComplete={handleAnalysisComplete} />
            <FeaturesGrid />
            <CTASection />
          </main>
        </div>
      )}
      
      {currentView === 'results' && analysisResult && (
        <AnalysisResults 
          analysisResult={analysisResult} 
          onBackToUpload={handleBackToUpload}
        />
      )}
    </QueryClientProvider>
  );
}
