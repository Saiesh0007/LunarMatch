import React from 'react';
import { Icon } from '../components/ui/Icon.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { StatusDot } from '../components/ui/StatusDot.jsx';
import { NAV_ITEMS } from '../data/navItems.js';
import { SidebarNavItem } from './SidebarNavItem.jsx';

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest border-r border-surface-container flex flex-col justify-between py-6 z-50">
      <div className="px-5">
        {/* Logo Section */}
        <div className="flex items-center gap-3 mb-10">
          <div className="h-8 w-8 rounded bg-surface-container-high border border-outline-variant flex items-center justify-center">
            <Icon name="radar" className="text-primary" />
          </div>
          <div>
            <div className="font-headline-md tracking-wider uppercase">LunarMatch</div>
            <div className="flex gap-2 items-center mt-0.5">
              <span className="font-label-sm text-on-surface-variant">WORKSTATION</span>
              <Badge variant="version" label="v2.4" />
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mb-4 font-label-md text-outline tracking-wider uppercase ml-4">Subsystems</div>
        <nav className="flex flex-col">
          {NAV_ITEMS.map((item) => (
            <SidebarNavItem key={item.path} item={item} />
          ))}
        </nav>
      </div>

      {/* Bottom Section */}
      <div className="px-5">
        {/* Node Status Widget */}
        <div className="bg-surface-container p-3 rounded-lg border border-surface-container-high mb-4">
          <div className="flex items-center justify-between mb-3 text-on-surface-variant">
            <span className="font-label-sm uppercase tracking-widest">Node Status</span>
            <div className="flex items-center gap-1">
              <Icon name="bolt" size="12px" />
              <span className="font-label-sm">42ms</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            <div className="bg-surface-container-low border border-outline-variant px-2 py-0.5 rounded text-xs font-label-sm text-primary">OHRC</div>
            <div className="bg-surface-container-low border border-outline-variant px-2 py-0.5 rounded text-xs font-label-sm text-primary">TMC-2</div>
            <div className="bg-surface-container-lowest border border-surface-container-high px-2 py-0.5 rounded text-xs font-label-sm text-outline-variant">IIRS</div>
          </div>
        </div>

        {/* User Identity */}
        <div className="flex items-center gap-3 bg-surface-container-lowest py-2">
          <div className="h-9 w-9 rounded-full bg-surface-container-high border border-outline-variant flex items-center justify-center font-headline-sm">
            ME
          </div>
          <div className="flex-1">
            <div className="font-headline-sm">Mission Engineer</div>
            <div className="font-label-sm text-on-surface-variant tracking-wider">SEC-LEVEL-4</div>
          </div>
          <button type="button" className="text-on-surface-variant hover:text-primary transition-colors h-8 w-8 flex items-center justify-center rounded bg-surface-container hover:bg-surface-container-high">
            <Icon name="logout" size="18px" />
          </button>
        </div>
      </div>
    </aside>
  );
}
