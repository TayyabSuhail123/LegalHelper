import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import HomePage from './components/HomePage';
import AnalysisResults from './components/AnalysisResults';
import { AnalysisResult } from './api/apiService';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

type AppView = 'upload' | 'results';

function App() {
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
        <HomePage onAnalysisComplete={handleAnalysisComplete} />
      )}
      
      {currentView === 'results' && analysisResult && (
        <AnalysisResults 
          analysisResult={analysisResult} 
          onBackToUpload={handleBackToUpload}
        />
      )}
      
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
