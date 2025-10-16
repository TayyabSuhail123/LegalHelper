'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from '../src/components/Header';
import HeroSection from '../src/components/HeroSection';
import FileUpload from '../src/components/FileUpload';
import FeaturesGrid from '../src/components/FeaturesGrid';
import CTASection from '../src/components/CTASection';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <Header />
        <main>
          <HeroSection />
          <FileUpload />
          <FeaturesGrid />
          <CTASection />
        </main>
      </div>
    </QueryClientProvider>
  );
}
