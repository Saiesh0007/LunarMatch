import { useState } from 'react';

export function useApiPing() {
  const [latency, setLatency] = useState(12);
  const [isPinging, setIsPinging] = useState(false);

  const pingServer = () => {
    setIsPinging(true);
    // Mock ping against current FastAPI socket expectation
    setTimeout(() => {
      // simulate random variation between 10ms - 25ms
      setLatency(10 + Math.floor(Math.random() * 15));
      setIsPinging(false);
    }, 600);
  };

  return { latency, isPinging, pingServer };
}
