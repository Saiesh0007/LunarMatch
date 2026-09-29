import { useState } from 'react';
import { apiClient } from '../../../api/client.js';

export function useApiPing() {
  const [latency, setLatency] = useState(12);
  const [isPinging, setIsPinging] = useState(false);
  const [error, setError] = useState(null);

  const pingServer = async () => {
    setIsPinging(true);
    setError(null);
    const start = performance.now();
    try {
      await apiClient.getHealth();
      const diff = Math.round(performance.now() - start);
      setLatency(diff);
    } catch (err) {
      console.error("Ping error:", err);
      setError(err.message);
      setLatency(null);
    } finally {
      setIsPinging(false);
    }
  };

  return { latency, isPinging, pingServer, error };
}
