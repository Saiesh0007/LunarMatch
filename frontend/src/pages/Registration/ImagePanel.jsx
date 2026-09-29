import React from 'react';
import { ImageViewport } from '../../components/ImageViewport.jsx';
import { twMerge } from 'tailwind-merge';

export function ImagePanel({ title, subtitle, file, onUpload, roleId, orderClass }) {
  return (
    <div className={twMerge("flex flex-col", orderClass)}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="font-label-md text-outline tracking-widest uppercase mb-1">{title}</div>
          <div className="font-headline-sm text-primary uppercase">{subtitle}</div>
        </div>
      </div>
      
      <ImageViewport file={file} roleId={roleId} label={title} onUpload={onUpload} />
    </div>
  );
}
