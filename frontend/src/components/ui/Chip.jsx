import React from 'react';
import { motion } from 'framer-motion';
import { twMerge } from 'tailwind-merge';

export function Chip({ label, active, onClick, className }) {
  return (
    <div 
      onClick={onClick}
      className={twMerge(
        "relative px-4 py-2 rounded-lg cursor-pointer transition-colors font-label-md uppercase tracking-wider text-center flex-1",
        active ? "text-black" : "text-on-surface-variant hover:bg-surface-container-high",
        className
      )}
    >
      {active && (
        <motion.div
          layoutId="chip-active"
          className="absolute inset-0 bg-primary rounded-lg z-0"
          initial={false}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      <span className="relative z-10 font-bold">{label}</span>
    </div>
  );
}
