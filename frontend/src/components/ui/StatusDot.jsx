import React from 'react';
import { twMerge } from 'tailwind-merge';
import { motion } from 'framer-motion';

export function StatusDot({ status = 'online', label, className }) {
  const isOnline = status === 'online';
  
  return (
    <div className={twMerge("flex items-center gap-2", className)}>
      <div className="relative flex h-2 w-2 items-center justify-center">
        {isOnline && (
          <motion.div 
            animate={{ scale: [1, 1.4, 1] }} 
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
            className="absolute rounded-full bg-primary opacity-30 h-3 w-3" 
          />
        )}
        <div className={twMerge(
          "h-1.5 w-1.5 rounded-full",
          isOnline ? "bg-primary" : "bg-outline-variant"
        )} />
      </div>
      {label && <span className="font-label-md text-on-surface-variant uppercase tracking-wider">{label}</span>}
    </div>
  );
}
