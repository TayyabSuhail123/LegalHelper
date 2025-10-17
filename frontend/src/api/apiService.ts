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
}

export const apiService = new ApiService();
export default apiService;
