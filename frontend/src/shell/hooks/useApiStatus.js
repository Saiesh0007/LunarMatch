import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client.js';

export function useApiStatus() {
  const { data, isError, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const start = performance.now();
      const res = await apiClient.getHealth();
      const ms = Math.round(performance.now() - start);
      return { ...res, ms };
    },
    refetchInterval: 10000, // Poll every 10s
    retry: 2,
    staleTime: 5000,
  });

  if (isLoading) return { status: 'offline', loading: true, ms: null };
  if (isError || !data) return { status: 'offline', loading: false, ms: null, error: error?.message };
  return { status: 'online', loading: false, ms: data.ms, service: data.service, version: data.version };
}
