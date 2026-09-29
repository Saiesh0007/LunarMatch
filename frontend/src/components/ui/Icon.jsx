import React from 'react';
import { clsx, typeClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Icon({ name, className, size = '20px' }) {
  return (
    <span 
      className={twMerge('material-symbols-outlined', className)} 
      style={{ fontSize: size }}
      aria-hidden="true"
    >
      {name}
    </span>
  );
}
