"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Header from "./components/Header";
import OverviewTab from "./components/OverviewTab";
import Footer from "./components/Footer";

// Non-default tabs and the export modal are code-split and loaded on demand
const TabLoading = () => <div className="card-box tab-loading" aria-busy="true">Loading module…</div>;
const StudioTab = dynamic(() => import("./components/StudioTab"), { loading: TabLoading });
const CorrespondenceTab = dynamic(() => import("./components/CorrespondenceTab"), { loading: TabLoading });
const RobustnessTab = dynamic(() => import("./components/RobustnessTab"), { loading: TabLoading });
const ArchitectureTab = dynamic(() => import("./components/ArchitectureTab"), { loading: TabLoading });
const ExportModal = dynamic(() => import("./components/ExportModal"));
import { checkHealth, StudioSession } from "./lib/api";

const TABS = ["overview", "studio", "correspondence", "robustness", "architecture"];

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);
  // Latest Studio run, consumed by the Correspondence and Robustness tabs
  const [session, setSession] = useState<StudioSession | null>(null);
  // Tabs stay mounted once visited so their state survives tab switches
  const [visitedTabs, setVisitedTabs] = useState<Set<string>>(() => new Set(["overview"]));

  if (!visitedTabs.has(activeTab)) setVisitedTabs(new Set(visitedTabs).add(activeTab));

  const tabPane = (tab: string, content: React.ReactNode) =>
    visitedTabs.has(tab) || activeTab === tab ? (
      <div key={tab} style={{ display: activeTab === tab ? "contents" : "none" }}>
        {content}
      </div>
    ) : null;

  const checkBackendHealth = async () => {
    setIsBackendOnline(await checkHealth());
  };

  useEffect(() => {
    let cancelled = false;
    checkHealth().then(online => {
      if (!cancelled) setIsBackendOnline(online);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // Sync active tab with URL hash (initial load and back/forward navigation)
  useEffect(() => {
    const syncFromHash = () => {
      const hash = window.location.hash.replace("#", "");
      if (TABS.includes(hash)) setActiveTab(hash);
    };
    const timer = setTimeout(syncFromHash, 0);
    window.addEventListener("hashchange", syncFromHash);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("hashchange", syncFromHash);
    };
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
        {tabPane("overview", <OverviewTab onNavigateTab={handleTabChange} />)}
        {tabPane("studio", <StudioTab isBackendOnline={isBackendOnline} onSessionChange={setSession} />)}
        {tabPane("correspondence", <CorrespondenceTab session={session} />)}
        {tabPane("robustness", <RobustnessTab session={session} isBackendOnline={isBackendOnline} />)}
        {tabPane("architecture", <ArchitectureTab />)}
      </main>

      {isExportOpen && <ExportModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />}

      <Footer onTabChange={handleTabChange} />
    </div>
  );
}
