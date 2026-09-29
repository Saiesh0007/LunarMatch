import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export function useApiStatus() {
  const { data, isError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      // Mock for now until FastAPI is connected
      return { status: 'online', ms: 12 };
      // const res = await axios.get('http://localhost:8000/health');
      // return res.data;
    },
    refetchInterval: 30000, // Every 30s
  });

  if (isError) return { status: 'offline' };
  return { status: 'online' };
}
