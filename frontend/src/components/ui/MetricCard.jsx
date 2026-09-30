import React, { useEffect } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';

export function MetricCard({ label, value, unit, subValue, highlight }) {
  // Extract number for count-up animation if possible
  const numValue = parseFloat(value);
  const isNumeric = !isNaN(numValue);
  
  const spring = useSpring(0, { bounce: 0, duration: 1500 });
  const displayValue = useTransform(spring, (current) => 
    isNumeric 
      ? (Number.isInteger(numValue) ? Math.floor(current) : current.toFixed(2)) 
      : value
  );

  useEffect(() => {
    if (isNumeric) {
      spring.set(numValue);
    }
  }, [numValue, spring]);

  return (
    <div className={`p-4 rounded-xl border flex flex-col justify-between h-full bg-surface-container hover:bg-surface-container-high transition-colors ${
      highlight ? 'border-outline-variant shadow-[0_0_15px_rgba(255,255,255,0.05)]' : 'border-surface-container-high'
    }`}>
      <div className="font-label-md text-outline tracking-widest uppercase mb-4">
        {label}
      </div>
      
      <div>
        <div className="flex items-baseline gap-1">
          <motion.div className="font-headline-lg text-3xl font-bold text-primary">
            {isNumeric ? displayValue : value}
          </motion.div>
          {unit && <span className="text-on-surface-variant font-label-md">{unit}</span>}
        </div>
        
        {subValue && (
          <div className="mt-2 font-label-sm text-outline-variant uppercase">
            {subValue}
          </div>
        )}
      </div>
    </div>
  );
}
