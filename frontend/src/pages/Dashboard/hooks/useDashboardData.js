import { useQuery } from '@tanstack/react-query';

export function useDashboardData() {
  // Mock data for UI development before FastAPI is connected
  
  const { data: pipelineStatus, isLoading: isPipelineLoading } = useQuery({
    queryKey: ['pipeline-status'],
    queryFn: async () => {
      return {
        jobs: [
          { id: 'JOB-261', inliers: 1402, rmse: 0.84, status: 'baseline' },
          { id: 'JOB-262', inliers: 905, rmse: 1.12, status: 'warning' },
          { id: 'JOB-263', inliers: 210, rmse: 4.88, status: 'degraded' },
          { id: 'JOB-264', inliers: 1845, rmse: 0.65, status: 'baseline' },
        ],
        kpis: {
          subpixelAccuracy: '0.84',
          uptime: '99.9%',
          processingTime: '240',
          totalAlignments: '124'
        }
      };
    }
  });

  return {
    pipelineStatus,
    isPipelineLoading
  };
}
