import React, { useState } from 'react';
import { Upload, FileText, Shield, Zap, ArrowRight, CheckCircle, AlertTriangle } from 'lucide-react';
import { useHealthCheck } from '../hooks/useApi';

const HomePage: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const { data: healthData, isLoading: healthLoading } = useHealthCheck();

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

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.type.includes('document')) {
        setUploadedFile(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0]);
    }
  };

  const features = [
    {
      icon: <Shield className="h-8 w-8 text-blue-500" />,
      title: "Risk Detection",
      description: "Advanced AI identifies potential legal risks and unfavorable terms"
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-500" />,
      title: "Instant Analysis",
      description: "Get comprehensive contract analysis in seconds, not hours"
    },
    {
      icon: <FileText className="h-8 w-8 text-green-500" />,
      title: "Smart Summaries",
      description: "Clear, actionable insights with highlighted key clauses"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">ContractCopilot</h1>
                <p className="text-purple-300 text-sm">AI-Powered Legal Document Risk Scanner</p>
              </div>
            </div>
            
            {/* Health Status */}
            <div className="flex items-center space-x-2 bg-black/30 px-4 py-2 rounded-lg">
              {healthLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-300 border-t-transparent"></div>
              ) : healthData?.status === 'healthy' ? (
                <CheckCircle className="h-4 w-4 text-green-400" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-red-400" />
              )}
              <span className="text-sm text-white">
                {healthLoading ? 'Checking...' : healthData?.status || 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-6">
            Analyze Legal Contracts with
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> AI Precision</span>
          </h2>
          <p className="text-xl text-purple-200 max-w-3xl mx-auto mb-8">
            Upload your contract and get instant AI-powered analysis identifying risks, 
            unfavorable terms, and actionable insights to protect your interests.
          </p>
        </div>

        {/* Upload Section */}
        <div className="max-w-2xl mx-auto mb-16">
          <div
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
              dragActive 
                ? 'border-blue-400 bg-blue-500/10 scale-105' 
                : uploadedFile
                ? 'border-green-400 bg-green-500/10'
                : 'border-purple-400/50 bg-black/20 hover:border-purple-400 hover:bg-black/30'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-upload"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf,.doc,.docx"
              onChange={handleFileSelect}
            />
            
            {uploadedFile ? (
              <div className="space-y-4">
                <div className="bg-green-500/20 p-4 rounded-lg border border-green-400/30">
                  <FileText className="h-12 w-12 text-green-400 mx-auto mb-2" />
                  <p className="text-green-300 font-medium">{uploadedFile.name}</p>
                  <p className="text-green-400/70 text-sm">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105">
                  <span>Analyze Contract</span>
                  <ArrowRight className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className={`h-16 w-16 mx-auto transition-colors duration-300 ${
                  dragActive ? 'text-blue-400' : 'text-purple-400'
                }`} />
                <div>
                  <p className="text-xl font-medium text-white mb-2">
                    {dragActive ? 'Drop your contract here' : 'Upload your legal contract'}
                  </p>
                  <p className="text-purple-300">
                    Drag and drop or <span className="text-blue-400 underline cursor-pointer">browse</span> to upload
                  </p>
                  <p className="text-purple-400/70 text-sm mt-2">
                    Supports PDF, DOC, DOCX files up to 10MB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-black/30 backdrop-blur-sm p-8 rounded-xl border border-white/10 hover:border-purple-400/50 transition-all duration-300 hover:transform hover:scale-105"
            >
              <div className="bg-black/40 p-4 rounded-lg w-fit mb-6">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-purple-200">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-500/20 to-purple-600/20 p-12 rounded-2xl border border-purple-400/30">
          <h3 className="text-3xl font-bold text-white mb-4">
            Ready to protect your business interests?
          </h3>
          <p className="text-purple-200 text-lg mb-6 max-w-2xl mx-auto">
            Join thousands of professionals who trust ContractCopilot for comprehensive contract analysis and risk assessment.
          </p>
          <button className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-10 py-4 rounded-lg font-medium text-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105">
            <span>Start Free Analysis</span>
            <ArrowRight className="h-6 w-6" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default HomePage;
