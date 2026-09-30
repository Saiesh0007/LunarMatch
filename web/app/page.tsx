"use client";

import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import OverviewTab from "./components/OverviewTab";
import StudioTab from "./components/StudioTab";
import CorrespondenceTab from "./components/CorrespondenceTab";
import RobustnessTab from "./components/RobustnessTab";
import ArchitectureTab from "./components/ArchitectureTab";
import ExportModal from "./components/ExportModal";
import Footer from "./components/Footer";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  const checkBackendHealth = async () => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 2000);
      const res = await fetch("http://127.0.0.1:8000/health", { signal: controller.signal });
      clearTimeout(timeout);
      if (res.ok) {
        setIsBackendOnline(true);
        return;
      }
    } catch {
      // Offline fallback
    }
    setIsBackendOnline(false);
  };

  useEffect(() => {
    checkBackendHealth();
    // Sync with URL hash
    const hash = window.location.hash.replace("#", "");
    if (hash && ["overview", "studio", "correspondence", "robustness", "architecture"].includes(hash)) {
      setActiveTab(hash);
    }
  }, []);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        onTabChange={handleTabChange}
        isBackendOnline={isBackendOnline}
        onCheckHealth={checkBackendHealth}
        onOpenExport={() => setIsExportOpen(true)}
      />

      <main className="main-content">
        {activeTab === "overview" && <OverviewTab onNavigateTab={handleTabChange} />}
        {activeTab === "studio" && <StudioTab />}
        {activeTab === "correspondence" && <CorrespondenceTab />}
        {activeTab === "robustness" && <RobustnessTab />}
        {activeTab === "architecture" && <ArchitectureTab />}
      </main>

      <ExportModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />

      <Footer onTabChange={handleTabChange} />
    </div>
  );
}
