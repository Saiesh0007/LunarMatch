import { useState, useEffect } from 'react';

export function useUtcClock() {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTimeStr(
        now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC'
      );
    };
    update();
    const interval = setInterval(update, 100); // 100ms for responsiveness, though rendering seconds
    return () => clearInterval(interval);
  }, []);

  return timeStr;
}
