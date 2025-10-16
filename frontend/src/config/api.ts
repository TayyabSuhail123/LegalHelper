import { Configuration } from '../api/generated/configuration';

// API Configuration
export const apiConfig = new Configuration({
  basePath: 'http://localhost:8000',
  baseOptions: {
    headers: {
      'Content-Type': 'application/json',
    },
  },
});

// API Base URL
export const API_BASE_URL = 'http://localhost:8000';
