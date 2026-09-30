import React from 'react';
import { twMerge } from 'tailwind-merge';

export function TechTag({ label, className }) {
  return (
    <span className={twMerge("inline-flex items-center px-2 py-1 rounded bg-surface-container-highest flex-wrap text-outline border border-surface-container", className)}>
      {label}
    </span>
  );
}
