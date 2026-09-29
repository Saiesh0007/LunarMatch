import { useState } from 'react';

export function useRobustnessLab() {
  const [selectedParam, setSelectedParam] = useState('illumination');
  const [selectedStep, setSelectedStep] = useState(0);
  const [isSweeping, setIsSweeping] = useState(false);
  const [stepsGranularity, setStepsGranularity] = useState('5'); // 3, 5, 7

  const handleRunSweep = () => {
    setIsSweeping(true);
    setTimeout(() => setIsSweeping(false), 2500); // mock
  };

  const dataSteps = [
    { degree: 0, rmse: 0.84, inliers: 1400 },
    { degree: 15, rmse: 0.95, inliers: 1205 },
    { degree: 30, rmse: 1.15, inliers: 980 },
    { degree: 45, rmse: 1.85, inliers: 650 },
    { degree: 60, rmse: 4.50, inliers: 210 },
  ];

  return {
    selectedParam, setSelectedParam,
    selectedStep, setSelectedStep,
    isSweeping, handleRunSweep,
    stepsGranularity, setStepsGranularity,
    dataSteps
  };
}
