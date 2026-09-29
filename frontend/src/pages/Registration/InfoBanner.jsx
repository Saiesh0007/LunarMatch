import React from 'react';
import { Icon } from '../../components/ui/Icon.jsx';

export function InfoBanner() {
  return (
    <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl mb-6 flex items-start gap-4">
      <Icon name="info" className="text-outline mt-0.5" />
      <div>
        <p className="font-body-lg text-on-surface-variant m-0">
          The <strong className="text-on-surface">Reference Frame</strong> sets the fixed coordinate system. The <strong className="text-on-surface">Target Frame</strong> will be warped and registered to match its perspective. Ensure base resolution is sufficient for sub-pixel feature detection.
        </p>
      </div>
    </div>
  );
}
