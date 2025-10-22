/**
 * API service for communicating with the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface UploadResponse {
  success: boolean;
  message: string;
  file_id: string;
  processing_status: string;
  estimated_processing_time?: number;
}

export interface FileDetails {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_timestamp: string;
  processing_status: string;
  extracted_text?: string;
  error_message?: string;
}

export interface ProcessingStatus {
  file_id: string;
  status: string;
  progress_percentage: number;
  current_step: string;
  estimated_time_remaining?: number;
  error_message?: string;
}

export interface DocumentClassification {
  document_type: string;
  confidence_score: number;
}

export interface LegalAnalysis {
  clauses_found: string[];
  payment_terms?: string;
  termination_clause?: string;
  liability_clause?: string;
  governing_law?: string;
  renewal_terms?: string;
}

export interface Risk {
  category: string;
  level: string;
  title: string;
  description: string;
  recommendation: string;
  confidence: number;
}

export interface RiskAssessment {
  overall_risk_score: number;
  overall_risk_level?: string;
  risks: Risk[];
  status: string;
}

export interface DocumentSummary {
  executive_summary: string;
  key_findings: string[];
}

export interface AnalysisResult {
  file_id: string;
  filename: string;
  status: string;
  progress_percentage: number;
  current_step?: string;
  created_at?: string;
  completed_at?: string;
  processing_time?: number;
  error?: string;
  failed_step?: string;
  extracted_text?: string;
  text_extraction_status?: string;
  
  // Multi-Agent Analysis Results
  // Document Summarizer Agent
  document_summary?: string;
  document_purpose?: string;
  key_parties?: string[];
  important_dates?: string[];
  
  // Risk Assessment Agent
  legal_risks?: Array<{
    category: string;
    severity: string;
    description: string;
    recommendation: string;
  }>;
  potential_liabilities?: string[];
  overall_risk_score?: number;
  overall_risk_level?: string;
  
  // Fraud Detection Agent
  suspicious_clauses?: Array<{
    clause: string;
    concern: string;
    severity: string;
  }>;
  hidden_fees?: string[];
  fraud_indicators?: string[];
  fraud_risk_score?: number;
  
  // Legal Advisor Agent
  legal_implications?: string[];
  rights_obligations?: {
    your_rights?: string[];
    your_obligations?: string[];
    other_party_rights?: string[];
    other_party_obligations?: string[];
  };
  compliance_issues?: string[];
  legal_advice?: string[];
  
  // Legacy fields for backward compatibility
  your_rights?: string[];
  their_obligations?: string[];
  potential_consequences?: string[];
  
  // Action Planner Agent
  immediate_actions?: Array<{
    action: string;
    priority: string;
    description: string;
  }> | string[];
  long_term_actions?: Array<{
    action: string;
    priority: string;
    description: string;
  }> | string[];
  deadlines?: Array<{
    deadline: string;
    description: string;
    priority: string;
  }>;
  recommendations?: string[];
  
  // Legacy fields for backward compatibility
  before_signing?: string[];
  long_term_considerations?: string[];
  recommended_timeline?: string;
  
  // Legacy fields (for backward compatibility)
  document_classification?: DocumentClassification;
  legal_analysis?: LegalAnalysis;
  analysis_status?: string;
  risk_assessment?: RiskAssessment;
  summary?: DocumentSummary;
  
  // Enhanced domain-driven fields (from UnifiedAnalysisService)
  domain_info?: {
    file_id: string;
    filename: string;
    size_mb: number;
    uploaded_by: string;
    analysis_started: boolean;
    can_retry: boolean;
  };
  
  domain_assessment?: {
    risk_level: string;
    confidence_score: number;
    risk_factors: string[];
    is_high_risk: boolean;
    is_critical_risk: boolean;
    requires_manual_review: boolean;
  };
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Upload a file for processing
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  /**
   * Get file details and extracted text
   */
  async getFileDetails(fileId: string): Promise<FileDetails> {
    const response = await fetch(`${this.baseUrl}/api/v1/files/files/${fileId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get file details' }));
      throw new Error(error.detail || 'Failed to get file details');
    }

    return response.json();
  }

  /**
   * Get processing status
   */
  async getProcessingStatus(fileId: string): Promise<ProcessingStatus> {
    const response = await fetch(`${this.baseUrl}/api/v1/files/status/${fileId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get status' }));
      throw new Error(error.detail || 'Failed to get status');
    }

    return response.json();
  }

  /**
   * Get supported file formats
   */
  async getSupportedFormats() {
    const response = await fetch(`${this.baseUrl}/api/v1/files/supported-formats`);

    if (!response.ok) {
      throw new Error('Failed to get supported formats');
    }

    return response.json();
  }

  /**
   * Health check
   */
  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/api/v1/health`);
    return response.json();
  }

  /**
   * Start AI analysis of a document using LangGraph workflow
   */
  async analyzeDocument(fileId: string): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/files/analyze/${fileId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(error.detail || 'Analysis failed');
    }

    return response.json();
  }

  /**
   * Get analysis result for a document
   */
  async getAnalysisResult(fileId: string): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/files/analysis/${fileId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get analysis result' }));
      throw new Error(error.detail || 'Failed to get analysis result');
    }

    return response.json();
  }
}

export const apiService = new ApiService();
export default apiService;
