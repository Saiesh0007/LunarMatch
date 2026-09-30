import React from 'react';
import { Icon } from './Icon.jsx';

export function SectionHeader({ icon, title, meta }) {
  return (
    <div className="flex items-center justify-between border-b border-surface-container-high pb-2 mb-4">
      <div className="flex items-center gap-2 text-on-surface">
        <Icon name={icon} size="18px" className="text-primary" />
        <h2 className="font-headline-md tracking-wider uppercase m-0">{title}</h2>
      </div>
      {meta && (
        <div className="font-label-md text-outline-variant tracking-widest uppercase">
          {meta}
        </div>
      )}
    </div>
  );
}
