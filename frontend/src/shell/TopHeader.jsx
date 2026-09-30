import React from 'react';
import { useLocation } from 'react-router-dom';
import { Icon } from '../components/ui/Icon.jsx';
import { StatusDot } from '../components/ui/StatusDot.jsx';
import { useUtcClock } from './hooks/useUtcClock.js';
import { useApiStatus } from './hooks/useApiStatus.js';
import { NAV_ITEMS } from '../data/navItems.js';

export function TopHeader() {
  const timeStr = useUtcClock();
  const apiStatus = useApiStatus();
  const location = useLocation();

  const activeItem = NAV_ITEMS.find(item =>
    item.path !== '/' ? location.pathname.startsWith(item.path) : location.pathname === '/'
  );
  const breadcrumb = `WORKSPACE › ${activeItem ? activeItem.name.toUpperCase() : 'UNKNOWN'}`;

  return (
    <header className="fixed top-0 left-72 right-0 h-16 z-40 bg-surface-container-lowest/90 backdrop-blur-md border-b border-surface-container flex items-center px-6 justify-between">
      <div className="flex items-center gap-6 text-on-surface-variant">
        <div className="font-label-lg tracking-widest text-on-surface flex items-center gap-2">
          <Icon name="folder_open" size="18px" />
          {breadcrumb}
        </div>
        <div className="hidden xl:flex items-center gap-2 bg-surface-container px-3 py-1 rounded border border-surface-container-high font-label-md">
          <Icon name="my_location" size="14px" />
          <span>78.5° S, 142.3° W (LUNAR ORBIT)</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="font-label-md bg-surface-container border border-surface-container-high px-3 py-1.5 rounded flex items-center gap-2">
          <Icon name="schedule" size="14px" className="text-outline" />
          <span className="tracking-widest font-mono">{timeStr}</span>
        </div>

        <div className="flex items-center gap-2 bg-surface-container border border-surface-container-high px-3 py-1 rounded">
          <StatusDot status={apiStatus.status} />
          <div className="flex flex-col ml-1">
            <span className="font-label-sm text-outline uppercase tracking-wider flex items-center gap-1">
              Backend {apiStatus.status === 'online' ? '(Connected)' : '(Offline)'}
            </span>
            <span className="font-mono text-[10px] text-primary">
              {apiStatus.ms != null ? `${apiStatus.ms}ms · 127.0.0.1:8000` : '127.0.0.1:8000'}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={() => window.open('http://127.0.0.1:8000/docs', '_blank')}
          className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high border border-outline-variant rounded hover:bg-surface-bright hover:border-outline transition-colors text-primary font-label-md ml-2 cursor-pointer"
        >
          <Icon name="terminal" size="16px" />
          <span>API DOCS</span>
        </button>
      </div>
    </header>
  );
}
