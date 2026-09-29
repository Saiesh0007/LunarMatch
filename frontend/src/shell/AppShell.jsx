import React from 'react';
import { useLocation, useOutlet } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './Sidebar.jsx';
import { TopHeader } from './TopHeader.jsx';

export default function AppShell() {
  const location = useLocation();
  const outlet = useOutlet();

  return (
    <div className="flex min-h-screen font-body-lg">
      <Sidebar />
      
      <div className="flex-1 flex flex-col ml-72">
        <TopHeader />
        
        <main className="flex-1 mt-16 p-lg bg-surface relative overflow-x-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="h-full w-full"
            >
              {outlet}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
