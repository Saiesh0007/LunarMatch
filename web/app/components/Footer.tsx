"use client";

import React from "react";

interface FooterProps {
  onTabChange: (tab: string) => void;
}

export default function Footer({ onTabChange }: FooterProps) {
  return (
    <footer className="app-footer">
      <div className="footer-left">
        <span>&copy; 2026 <strong>LUNARMATCH</strong> &bull; Team Spectrum</span>
        <span>ISRO Smart India Hackathon &bull; Problem Statement 26166</span>
      </div>
      <div className="footer-right">
        <button className="footer-btn" onClick={() => onTabChange("overview")}>Overview</button>
        <button className="footer-btn" onClick={() => onTabChange("studio")}>Studio</button>
        <button className="footer-btn" onClick={() => onTabChange("correspondence")}>Correspondences</button>
        <button className="footer-btn" onClick={() => onTabChange("robustness")}>Robustness</button>
        <button className="footer-btn" onClick={() => onTabChange("architecture")}>Architecture</button>
      </div>
    </footer>
  );
}
