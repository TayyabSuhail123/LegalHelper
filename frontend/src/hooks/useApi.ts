import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  });
};

// Detailed health check hook
export const useDetailedHealthCheck = () => {
  return useQuery({
    queryKey: ['health', 'detailed'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/health/detailed`);
      if (!response.ok) {
        throw new Error('Detailed health check failed');
      }
      return response.json();
    },
    refetchInterval: 60000, // Refetch every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  });
};
