"use client";

import React from "react";
import Image from "next/image";

interface HeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isBackendOnline: boolean;
  onCheckHealth: () => void;
  onOpenExport: () => void;
}

export default function Header({
  activeTab,
  onTabChange,
  isBackendOnline,
  onCheckHealth,
  onOpenExport
}: HeaderProps) {
  return (
    <header className="top-header">
      <div className="brand-wrapper">
        <Image
          src="/assets/icons/app_logo.png"
          alt="LunarMatch Logo"
          width={28}
          height={28}
          className="brand-logo-img"
          priority
        />
        <div className="brand-titles">
          <div className="brand-title">
            <span>LUNARMATCH</span>
            <span className="tag-badge badge-white">PS 26166</span>
          </div>
          <span className="brand-subtitle">ISRO SIH 2026 &bull; SPACE TECHNOLOGY</span>
        </div>
      </div>

      <nav className="nav-tabs" aria-label="Main Navigation">
        <button
          className={`nav-tab-btn ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => onTabChange("overview")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          </svg>
          Overview
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "studio" ? "active" : ""}`}
          onClick={() => onTabChange("studio")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <line x1="12" y1="8" x2="12" y2="16" />
            <line x1="8" y1="12" x2="16" y2="12" />
          </svg>
          Studio
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "correspondence" ? "active" : ""}`}
          onClick={() => onTabChange("correspondence")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="6" cy="6" r="3" />
            <circle cx="18" cy="18" r="3" />
            <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
          </svg>
          Correspondences
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "robustness" ? "active" : ""}`}
          onClick={() => onTabChange("robustness")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
          </svg>
          Robustness
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "architecture" ? "active" : ""}`}
          onClick={() => onTabChange("architecture")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
          Architecture
        </button>
      </nav>

      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <div className="status-pill" title="Backend Health Status">
          <span className={`pulse-dot ${isBackendOnline ? "" : "dot-offline"}`} />
          <span>{isBackendOnline ? "FASTAPI: ONLINE" : "FLIGHT SIMULATION"}</span>
          <button
            className="btn-secondary-action"
            style={{ padding: "2px 6px", fontSize: "0.65rem" }}
            onClick={onCheckHealth}
          >
            CHECK
          </button>
        </div>

        <button className="btn-secondary-action" onClick={onOpenExport}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Export
        </button>
      </div>
    </header>
  );
}
