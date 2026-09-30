import React from 'react';
import { motion } from 'framer-motion';
import { twMerge } from 'tailwind-merge';

export function Chip({ label, active, onClick, className, layoutId = "chip-active" }) {
  return (
    <div 
      onClick={onClick}
      className={twMerge(
        "relative px-4 py-2 rounded cursor-pointer transition-colors font-label-md uppercase tracking-wider text-center flex-1",
        active ? "text-on-primary font-bold" : "text-on-surface-variant hover:bg-surface-container-high",
        className
      )}
    >
      {active && (
        <motion.div
          layoutId={layoutId}
          className="absolute inset-0 bg-primary rounded z-0"
          initial={false}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      <span className="relative z-10">{label}</span>
    </div>
  );
}
