import React from 'react';
import { Icon } from '../../components/ui/Icon.jsx';
import { TechTag } from '../../components/ui/TechTag.jsx';

export function PipelineStageCard({ stage, isLast }) {
  return (
    <div className="flex relative">
      {!isLast && (
         <div className="absolute left-[38px] top-12 bottom-0 w-px bg-surface-container-high z-0" />
      )}
      
      <div className="w-20 pt-4 relative z-10">
        <div className="h-10 w-10 text-xs font-mono rounded bg-surface-container-lowest border border-surface-container-high flex flex-col items-center justify-center text-outline-variant mx-4 group-hover:border-outline transition-colors">
          <span className="opacity-50">STG</span>
          <span className="text-on-surface">{stage.id}</span>
        </div>
      </div>
      
      <div className="flex-1 pb-8">
        <div className="bg-surface-container border border-surface-container-high p-5 rounded-xl hover:bg-surface-container-high transition-colors group">
          <div className="flex items-center justify-between mb-3">
             <div className="flex items-center gap-3">
               <Icon name={stage.icon} size="20px" className="text-primary" />
               <h3 className="font-headline-md tracking-wider uppercase text-on-surface m-0 group-hover:text-primary transition-colors">{stage.title}</h3>
             </div>
          </div>
          
          <p className="font-body-md text-on-surface-variant mb-4">{stage.description}</p>
          
          <div className="flex flex-wrap gap-2">
            {stage.tags.map(tag => (
               <TechTag key={tag} label={tag} className="text-xs" />
            ))}
          </div>
        </div>
        
        {!isLast && (
           <div className="mt-4 ml-6 relative z-10 w-max bg-surface text-surface-container-high">
              <Icon name="arrow_downward" size="20px" className="animate-pulse" />
           </div>
        )}
      </div>
    </div>
  );
}
