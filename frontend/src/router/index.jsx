import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import AppShell from '../shell/AppShell.jsx';
import Dashboard from '../pages/Dashboard/Dashboard.jsx';

// For now, only Dashboard is routed. 
// Standard modular scaling for the other 4 pages later.

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> }
    ],
  },
]);
