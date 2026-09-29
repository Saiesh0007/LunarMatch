import React from 'react';
import { motion } from 'framer-motion';
import { twMerge } from 'tailwind-merge';
import { Icon } from './Icon.jsx';

export function Button({ 
  children, 
  variant = 'primary', 
  className, 
  icon, 
  loading = false, 
  onClick, 
  type = 'button',
  disabled = false
}) {
  const baseClasses = "inline-flex items-center justify-center font-label-lg tracking-widest uppercase transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-primary text-black rounded-full px-5 py-2.5 hover:bg-surface-container-highest",
    ghost: "bg-transparent border border-outline-variant text-on-surface rounded-lg px-4 py-2 hover:bg-surface-container",
    icon: "bg-surface-container-lowest text-on-surface border border-surface-container h-10 w-10 rounded-full hover:bg-surface-container-high",
  };

  return (
    <motion.button 
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
      className={twMerge(baseClasses, variants[variant], className)}
    >
      {loading ? (
        <Icon name="progress_activity" className="animate-spin mr-2" size="18px" />
      ) : icon ? (
        <Icon name={icon} className={children ? "mr-2" : ""} size="18px" />
      ) : null}
      {children}
    </motion.button>
  );
}
