import { useQuery } from '@tanstack/react-query';
import { HealthApi } from '../api/generated/api/health-api';
import { apiConfig } from '../config/api';

// Initialize API instances
const healthApi = new HealthApi(apiConfig);

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await healthApi.healthCheckApiV1HealthGet();
      return response.data;
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
      const response =
        await healthApi.detailedHealthCheckApiV1HealthDetailedGet();
      return response.data;
    },
    refetchInterval: 60000, // Refetch every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  });
};
