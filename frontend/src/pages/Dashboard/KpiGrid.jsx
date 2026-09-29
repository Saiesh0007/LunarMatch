import React from 'react';
import { motion } from 'framer-motion';
import { MetricCard } from '../../components/ui/MetricCard.jsx';

export function KpiGrid({ data }) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', duration: 0.5 } }
  };

  const kpis = data || { subpixelAccuracy: '0', uptime: '0', processingTime: '0', totalAlignments: '0' };

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
    >
      <motion.div variants={item}>
        <MetricCard highlight label="RMSE Accuracy" value={kpis.subpixelAccuracy} unit="px" subValue="TOLERANCE < 1.0px" />
      </motion.div>
      <motion.div variants={item}>
        <MetricCard label="System Uptime" value={kpis.uptime} subValue="ORBITAL LOCK SECURED" />
      </motion.div>
      <motion.div variants={item}>
        <MetricCard label="Avg Pipeline Latency" value={kpis.processingTime} unit="ms" subValue="CPU INFERENCE MODE" />
      </motion.div>
      <motion.div variants={item}>
        <MetricCard label="Total Matches" value={kpis.totalAlignments} subValue="VALIDATED INLIER SETS" />
      </motion.div>
    </motion.div>
  );
}
