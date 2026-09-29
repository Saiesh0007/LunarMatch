import React from 'react';
import { twMerge } from 'tailwind-merge';

export function Badge({ label, variant = 'code', className }) {
  const baseClasses = "inline-flex items-center px-1.5 py-0.5 rounded-sm font-label-md";
  const variants = {
    code: "bg-surface-container-high text-on-surface border border-outline-variant",
    version: "bg-primary text-on-primary bg-opacity-90 font-bold",
    status: "bg-surface-container text-on-surface-variant",
    error: "bg-error-container text-on-error-container border border-error",
  };

  return (
    <span className={twMerge(baseClasses, variants[variant], className)}>
      {label}
    </span>
  );
}
