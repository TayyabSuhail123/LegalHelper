'use client';

import React from 'react';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle2,
  CheckCircle, 
  XCircle, 
  Shield, 
  Scale, 
  Clock,
  Download,
  ArrowLeft,
  Star,
  TrendingUp,
  Users,
  Calendar,
  Eye,
  AlertCircle,
  DollarSign,
  BookOpen,
  UserCheck,
  Target,
  CheckSquare,
  ListTodo
} from 'lucide-react';
import { AnalysisResult, Risk } from '../api/apiService';

interface AnalysisResultsProps {
  analysisResult: AnalysisResult;
  onBackToUpload: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ 
  analysisResult, 
  onBackToUpload 
}) => {
  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return 'text-green-400 bg-green-400/20 border-green-400/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-400/20 border-yellow-400/30';
      case 'high':
        return 'text-red-400 bg-red-400/20 border-red-400/30';
      case 'critical':
        return 'text-red-500 bg-red-500/20 border-red-500/30';
      default:
        return 'text-gray-400 bg-gray-400/20 border-gray-400/30';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return <CheckCircle2 className="h-5 w-5" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5" />;
      case 'high':
        return <XCircle className="h-5 w-5" />;
      case 'critical':
        return <AlertCircle className="h-5 w-5" />;
      default:
        return <Shield className="h-5 w-5" />;
    }
  };

  const formatProcessingTime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    return `${seconds.toFixed(2)}s`;
  };

  const formatRiskScore = (score?: number) => {
    if (!score) return 'N/A';
    return `${score.toFixed(1)}/10`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={onBackToUpload}
            className="flex items-center space-x-2 text-purple-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Upload</span>
          </button>
          
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
              <Download className="h-4 w-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>

        {/* Document Info Header */}
        <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 mb-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-purple-500/20 p-3 rounded-lg">
                <FileText className="h-8 w-8 text-purple-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white mb-2">
                  Legal Document Analysis
                </h1>
                <p className="text-purple-200">
                  {analysisResult.filename}
                </p>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
                  <span>File ID: {analysisResult.file_id}</span>
                  <span>•</span>
                  <span>Processing Time: {formatProcessingTime(analysisResult.processing_time)}</span>
                  <span>•</span>
                  <span>Completed: {analysisResult.completed_at ? new Date(analysisResult.completed_at).toLocaleString() : 'N/A'}</span>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border ${
                analysisResult.status === 'completed' 
                  ? 'text-green-400 bg-green-400/20 border-green-400/30'
                  : 'text-gray-400 bg-gray-400/20 border-gray-400/30'
              }`}>
                {analysisResult.status === 'completed' ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Clock className="h-4 w-4" />
                )}
                <span className="capitalize">{analysisResult.status}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Document Summary */}
            {analysisResult.document_summary && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <BookOpen className="h-6 w-6 text-purple-400" />
                  <span>Document Summary</span>
                </h2>
                
                <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4 mb-4">
                  <p className="text-purple-100 leading-relaxed">
                    {analysisResult.document_summary}
                  </p>
                </div>

                {analysisResult.document_purpose && (
                  <div className="mb-4">
                    <h3 className="text-white font-medium mb-2">Document Purpose:</h3>
                    <p className="text-gray-300">{analysisResult.document_purpose}</p>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysisResult.key_parties && analysisResult.key_parties.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <Users className="h-4 w-4" />
                        <span>Key Parties</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.key_parties.map((party, index) => (
                          <li key={index} className="text-gray-300 text-sm">• {party}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.important_dates && analysisResult.important_dates.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <Calendar className="h-4 w-4" />
                        <span>Important Dates</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.important_dates.map((date, index) => (
                          <li key={index} className="text-gray-300 text-sm">• {date}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Legal Risks */}
            {analysisResult.legal_risks && analysisResult.legal_risks.length > 0 && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <AlertTriangle className="h-6 w-6 text-red-400" />
                  <span>Legal Risks</span>
                </h2>
                
                <div className="space-y-4">
                  {analysisResult.legal_risks.map((risk, index) => (
                    <div key={index} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-white font-medium">{risk.category}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          getRiskLevelColor(risk.severity)
                        }`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm mb-2">{risk.description}</p>
                      <p className="text-blue-300 text-sm">
                        <strong>Recommendation:</strong> {risk.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fraud Detection */}
            {((analysisResult.suspicious_clauses && analysisResult.suspicious_clauses.length > 0) ||
              (analysisResult.hidden_fees && analysisResult.hidden_fees.length > 0) ||
              (analysisResult.fraud_indicators && analysisResult.fraud_indicators.length > 0)) && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <Eye className="h-6 w-6 text-orange-400" />
                  <span>Fraud Detection</span>
                </h2>
                
                <div className="space-y-4">
                  {analysisResult.suspicious_clauses && analysisResult.suspicious_clauses.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Suspicious Clauses:</h3>
                      <div className="space-y-2">
                        {analysisResult.suspicious_clauses.map((clause, index) => (
                          <div key={index} className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3">
                            <p className="text-gray-300 text-sm mb-1">{clause.clause}</p>
                            <p className="text-orange-300 text-xs">{clause.concern}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult.hidden_fees && analysisResult.hidden_fees.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <DollarSign className="h-4 w-4" />
                        <span>Hidden Fees Detected:</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.hidden_fees.map((fee, index) => (
                          <li key={index} className="text-red-300 text-sm">• {fee}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.fraud_indicators && analysisResult.fraud_indicators.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Fraud Indicators:</h3>
                      <ul className="space-y-1">
                        {analysisResult.fraud_indicators.map((indicator, index) => (
                          <li key={index} className="text-yellow-300 text-sm">⚠ {indicator}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Legal Implications */}
            {((analysisResult.legal_implications && analysisResult.legal_implications.length > 0) ||
              (analysisResult.rights_obligations && (
                (analysisResult.rights_obligations.your_rights && analysisResult.rights_obligations.your_rights.length > 0) ||
                (analysisResult.rights_obligations.your_obligations && analysisResult.rights_obligations.your_obligations.length > 0) ||
                (analysisResult.rights_obligations.other_party_rights && analysisResult.rights_obligations.other_party_rights.length > 0) ||
                (analysisResult.rights_obligations.other_party_obligations && analysisResult.rights_obligations.other_party_obligations.length > 0)
              )) ||
              (analysisResult.your_rights && analysisResult.your_rights.length > 0) ||
              (analysisResult.their_obligations && analysisResult.their_obligations.length > 0) ||
              (analysisResult.potential_consequences && analysisResult.potential_consequences.length > 0) ||
              (analysisResult.compliance_issues && analysisResult.compliance_issues.length > 0) ||
              (analysisResult.legal_advice && analysisResult.legal_advice.length > 0)) && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <Scale className="h-6 w-6 text-blue-400" />
                  <span>Legal Implications</span>
                </h2>
                
                <div className="space-y-4">
                  {analysisResult.legal_implications && analysisResult.legal_implications.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Legal Implications:</h3>
                      <ul className="space-y-1">
                        {analysisResult.legal_implications.map((implication, index) => (
                          <li key={index} className="text-gray-300 text-sm">• {implication}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* New organized rights_obligations structure */}
                    {analysisResult.rights_obligations?.your_rights && analysisResult.rights_obligations.your_rights.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                          <UserCheck className="h-4 w-4" />
                          <span>Your Rights:</span>
                        </h3>
                        <ul className="space-y-1">
                          {analysisResult.rights_obligations.your_rights.map((right, index) => (
                            <li key={index} className="text-green-300 text-sm">✓ {right}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.rights_obligations?.your_obligations && analysisResult.rights_obligations.your_obligations.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2">Your Obligations:</h3>
                        <ul className="space-y-1">
                          {analysisResult.rights_obligations.your_obligations.map((obligation, index) => (
                            <li key={index} className="text-yellow-300 text-sm">⚠ {obligation}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.rights_obligations?.other_party_rights && analysisResult.rights_obligations.other_party_rights.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2">Other Party Rights:</h3>
                        <ul className="space-y-1">
                          {analysisResult.rights_obligations.other_party_rights.map((right, index) => (
                            <li key={index} className="text-blue-300 text-sm">• {right}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.rights_obligations?.other_party_obligations && analysisResult.rights_obligations.other_party_obligations.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2">Their Obligations:</h3>
                        <ul className="space-y-1">
                          {analysisResult.rights_obligations.other_party_obligations.map((obligation, index) => (
                            <li key={index} className="text-blue-300 text-sm">• {obligation}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Legacy compatibility */}
                    {analysisResult.your_rights && analysisResult.your_rights.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                          <UserCheck className="h-4 w-4" />
                          <span>Your Rights:</span>
                        </h3>
                        <ul className="space-y-1">
                          {analysisResult.your_rights.map((right, index) => (
                            <li key={index} className="text-green-300 text-sm">✓ {right}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.their_obligations && analysisResult.their_obligations.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2">Their Obligations:</h3>
                        <ul className="space-y-1">
                          {analysisResult.their_obligations.map((obligation, index) => (
                            <li key={index} className="text-blue-300 text-sm">• {obligation}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysisResult.potential_consequences && analysisResult.potential_consequences.length > 0 && (
                      <div>
                        <h3 className="text-white font-medium mb-2">Potential Consequences:</h3>
                        <ul className="space-y-1">
                          {analysisResult.potential_consequences.map((consequence, index) => (
                            <li key={index} className="text-yellow-300 text-sm">⚠ {consequence}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {analysisResult.compliance_issues && analysisResult.compliance_issues.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Compliance Requirements:</h3>
                      <ul className="space-y-1">
                        {analysisResult.compliance_issues.map((issue, index) => (
                          <li key={index} className="text-orange-300 text-sm">📋 {issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.legal_advice && analysisResult.legal_advice.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Legal Advice:</h3>
                      <ul className="space-y-1">
                        {analysisResult.legal_advice.map((advice, index) => (
                          <li key={index} className="text-purple-300 text-sm">💡 {advice}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Action Plan */}
            {((analysisResult.immediate_actions && analysisResult.immediate_actions.length > 0) ||
              (analysisResult.long_term_actions && analysisResult.long_term_actions.length > 0) ||
              (analysisResult.before_signing && analysisResult.before_signing.length > 0) ||
              (analysisResult.long_term_considerations && analysisResult.long_term_considerations.length > 0) ||
              (analysisResult.deadlines && analysisResult.deadlines.length > 0) ||
              (analysisResult.recommendations && analysisResult.recommendations.length > 0)) && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <Target className="h-6 w-6 text-green-400" />
                  <span>Action Plan</span>
                </h2>
                
                <div className="space-y-4">
                  {analysisResult.immediate_actions && analysisResult.immediate_actions.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <CheckSquare className="h-4 w-4 text-red-400" />
                        <span>Immediate Actions:</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.immediate_actions.map((action, index) => {
                          if (typeof action === 'string') {
                            return <li key={index} className="text-red-300 text-sm">🚨 {action}</li>;
                          } else {
                            return (
                              <li key={index} className="text-red-300 text-sm">
                                <div className="font-medium">🚨 {action.action}</div>
                                <div className="text-xs text-gray-400 ml-4">{action.description}</div>
                                <div className="text-xs text-yellow-300 ml-4">Priority: {action.priority}</div>
                              </li>
                            );
                          }
                        })}
                      </ul>
                    </div>
                  )}

                  {analysisResult.long_term_actions && analysisResult.long_term_actions.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <ListTodo className="h-4 w-4 text-blue-400" />
                        <span>Long-term Actions:</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.long_term_actions.map((action, index) => {
                          if (typeof action === 'string') {
                            return <li key={index} className="text-blue-300 text-sm">💡 {action}</li>;
                          } else {
                            return (
                              <li key={index} className="text-blue-300 text-sm">
                                <div className="font-medium">💡 {action.action}</div>
                                <div className="text-xs text-gray-400 ml-4">{action.description}</div>
                                <div className="text-xs text-yellow-300 ml-4">Priority: {action.priority}</div>
                              </li>
                            );
                          }
                        })}
                      </ul>
                    </div>
                  )}

                  {analysisResult.before_signing && analysisResult.before_signing.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <ListTodo className="h-4 w-4 text-yellow-400" />
                        <span>Before Signing:</span>
                      </h3>
                      <ul className="space-y-1">
                        {analysisResult.before_signing.map((item, index) => (
                          <li key={index} className="text-yellow-300 text-sm">⚠ {item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.long_term_considerations && analysisResult.long_term_considerations.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">Long-term Considerations:</h3>
                      <ul className="space-y-1">
                        {analysisResult.long_term_considerations.map((consideration, index) => (
                          <li key={index} className="text-blue-300 text-sm">💡 {consideration}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.deadlines && analysisResult.deadlines.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2 flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-orange-400" />
                        <span>Important Deadlines:</span>
                      </h3>
                      <div className="space-y-2">
                        {analysisResult.deadlines.map((deadline, index) => (
                          <div key={index} className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3">
                            <div className="flex justify-between items-start">
                              <span className="text-orange-300 font-medium">{deadline.description}</span>
                              <span className={`px-2 py-1 rounded text-xs ${
                                deadline.priority === 'HIGH' ? 'bg-red-500/20 text-red-300' :
                                deadline.priority === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-300' :
                                'bg-green-500/20 text-green-300'
                              }`}>
                                {deadline.priority}
                              </span>
                            </div>
                            <div className="text-white text-sm mt-1">📅 {deadline.deadline}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                    <div>
                      <h3 className="text-white font-medium mb-2">General Recommendations:</h3>
                      <ul className="space-y-1">
                        {analysisResult.recommendations.map((recommendation, index) => (
                          <li key={index} className="text-purple-300 text-sm">📝 {recommendation}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysisResult.recommended_timeline && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
                      <h3 className="text-white font-medium mb-1">Recommended Timeline:</h3>
                      <p className="text-green-300 text-sm">{analysisResult.recommended_timeline}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            
            {/* Risk Assessment Summary */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Shield className="h-6 w-6 text-purple-400" />
                <span>Risk Summary</span>
              </h2>
              
              {/* Overall Risk Score */}
              {analysisResult.overall_risk_score !== undefined && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Legal Risk</span>
                    <span className="text-2xl font-bold text-white">
                      {formatRiskScore(analysisResult.overall_risk_score)}
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
                    <div 
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        analysisResult.overall_risk_score <= 3
                          ? 'bg-gradient-to-r from-green-500 to-green-400'
                          : analysisResult.overall_risk_score <= 6
                          ? 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                          : 'bg-gradient-to-r from-red-500 to-red-400'
                      }`}
                      style={{ 
                        width: `${Math.min((analysisResult.overall_risk_score / 10) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                  
                  {analysisResult.overall_risk_level && (
                    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border ${
                      getRiskLevelColor(analysisResult.overall_risk_level)
                    }`}>
                      {getRiskIcon(analysisResult.overall_risk_level)}
                      <span className="font-medium capitalize">
                        {analysisResult.overall_risk_level} Risk
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Fraud Risk Score */}
              {analysisResult.fraud_risk_score !== undefined && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Fraud Risk</span>
                    <span className="text-2xl font-bold text-white">
                      {formatRiskScore(analysisResult.fraud_risk_score)}
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
                    <div 
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        analysisResult.fraud_risk_score <= 3
                          ? 'bg-gradient-to-r from-green-500 to-green-400'
                          : analysisResult.fraud_risk_score <= 6
                          ? 'bg-gradient-to-r from-orange-500 to-orange-400'
                          : 'bg-gradient-to-r from-red-500 to-red-400'
                      }`}
                      style={{ 
                        width: `${Math.min((analysisResult.fraud_risk_score / 10) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Enhanced Domain Assessment (if available) */}
              {analysisResult.domain_assessment && (
                <div className="mt-6 p-4 bg-purple-900/30 rounded-lg border border-purple-700/50">
                  <h3 className="text-lg font-semibold text-purple-300 mb-3 flex items-center space-x-2">
                    <Shield className="h-5 w-5" />
                    <span>Enhanced Risk Assessment</span>
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-300 text-sm">Risk Level:</span>
                      <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border ml-2 ${
                        analysisResult.domain_assessment.risk_level === 'low' 
                          ? 'border-green-500/50 bg-green-900/20 text-green-300'
                          : analysisResult.domain_assessment.risk_level === 'medium'
                          ? 'border-yellow-500/50 bg-yellow-900/20 text-yellow-300'
                          : 'border-red-500/50 bg-red-900/20 text-red-300'
                      }`}>
                        <span className="font-medium capitalize">
                          {analysisResult.domain_assessment.risk_level}
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <span className="text-gray-300 text-sm">Confidence:</span>
                      <span className="text-white font-medium ml-2">
                        {Math.round(analysisResult.domain_assessment.confidence_score * 100)}%
                      </span>
                    </div>
                  </div>

                  {analysisResult.domain_assessment.risk_factors && analysisResult.domain_assessment.risk_factors.length > 0 && (
                    <div className="mt-4">
                      <span className="text-gray-300 text-sm">Key Risk Factors:</span>
                      <div className="mt-2 space-y-1">
                        {analysisResult.domain_assessment.risk_factors.map((factor, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <AlertTriangle className="h-4 w-4 text-yellow-400 flex-shrink-0" />
                            <span className="text-gray-300 text-sm">{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="mt-4 flex flex-wrap gap-2">
                    {analysisResult.domain_assessment.is_high_risk && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-900/50 text-red-300 border border-red-700/50">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        High Risk
                      </span>
                    )}
                    {analysisResult.domain_assessment.is_critical_risk && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-900/70 text-red-200 border border-red-600/50">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Critical Risk
                      </span>
                    )}
                    {analysisResult.domain_assessment.requires_manual_review && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-900/50 text-purple-300 border border-purple-700/50">
                        <Eye className="h-3 w-3 mr-1" />
                        Manual Review Required
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Enhanced File Information (if available) */}
            {analysisResult.domain_info && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 mb-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                  <FileText className="h-6 w-6 text-purple-400" />
                  <span>File Details</span>
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <span className="text-gray-400 text-sm">File Size:</span>
                    <p className="text-white font-medium">{analysisResult.domain_info.size_mb.toFixed(2)} MB</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-sm">Processed By:</span>
                    <p className="text-white font-medium">{analysisResult.domain_info.uploaded_by}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-sm">Status:</span>
                    <div className="flex items-center space-x-2">
                      {analysisResult.domain_info.analysis_started ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-900/50 text-green-300 border border-green-700/50">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Analysis Started
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-900/50 text-gray-300 border border-gray-700/50">
                          Pending
                        </span>
                      )}
                      {analysisResult.domain_info.can_retry && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-900/50 text-blue-300 border border-blue-700/50">
                          Retryable
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Processing Details */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Processing Details</h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-white capitalize">{analysisResult.status}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-400">Progress:</span>
                  <span className="text-white">{analysisResult.progress_percentage}%</span>
                </div>
                
                {analysisResult.current_step && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Step:</span>
                    <span className="text-white">{analysisResult.current_step}</span>
                  </div>
                )}
                
                {analysisResult.processing_time && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Processing Time:</span>
                    <span className="text-white">{formatProcessingTime(analysisResult.processing_time)}</span>
                  </div>
                )}

                {analysisResult.created_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Started:</span>
                    <span className="text-white">{new Date(analysisResult.created_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;