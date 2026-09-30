import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Icon } from '../components/ui/Icon.jsx';
import { twMerge } from 'tailwind-merge';

export function SidebarNavItem({ item }) {
  return (
    <NavLink to={item.path} end={item.path === '/'}>
      {({ isActive }) => (
        <motion.div 
          whileHover={{ x: 2 }}
          className={twMerge(
            "relative flex flex-col gap-1 px-4 py-2.5 rounded-lg mb-2 transition-colors cursor-pointer",
            isActive ? "text-primary" : "text-on-surface-variant hover:bg-surface-container"
          )}
        >
          {isActive && (
            <motion.div
              layoutId="active-nav-capsule"
              className="absolute inset-0 bg-surface-container-high rounded-lg z-0"
              initial={false}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            />
          )}
          
          <div className="relative z-10 font-label-sm tracking-widest opacity-80 uppercase">
            {item.codeLabel}
          </div>
          <div className="relative z-10 flex items-center gap-3">
            <Icon name={item.icon} size="18px" />
            <span className={twMerge("font-headline-sm", isActive && "font-bold")}>
              {item.name}
            </span>
          </div>
        </motion.div>
      )}
    </NavLink>
  );
}
