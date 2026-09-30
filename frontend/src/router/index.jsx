import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import AppShell from '../shell/AppShell.jsx';
import Dashboard from '../pages/Dashboard/Dashboard.jsx';
import Registration from '../pages/Registration/Registration.jsx';
// Placeholders for the remaining pages
import RobustnessLab from '../pages/RobustnessLab/RobustnessLab.jsx';
import Capabilities from '../pages/Capabilities/Capabilities.jsx';
import MissionInfo from '../pages/MissionInfo/MissionInfo.jsx';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'registration', element: <Registration /> },
      { path: 'robustness-lab', element: <RobustnessLab /> },
      { path: 'capabilities', element: <Capabilities /> },
      { path: 'mission-info', element: <MissionInfo /> }
    ],
  },
]);
