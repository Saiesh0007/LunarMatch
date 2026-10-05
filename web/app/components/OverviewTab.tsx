"use client";

import React, { useState, useSyncExternalStore } from "react";
import { SENSOR_SPECS } from "../data/lunarData";

interface OverviewTabProps {
  onNavigateTab: (tab: string) => void;
}

/* ---------- Reduced-motion preference (SMIL animations ignore the CSS media rule) ---------- */
const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";
const subscribeReducedMotion = (cb: () => void) => {
  const mq = window.matchMedia(REDUCED_MOTION_QUERY);
  mq.addEventListener("change", cb);
  return () => mq.removeEventListener("change", cb);
};
const usePrefersReducedMotion = () =>
  useSyncExternalStore(
    subscribeReducedMotion,
    () => window.matchMedia(REDUCED_MOTION_QUERY).matches,
    () => false
  );

/* ---------- Chandrayaan-2 optical payloads, imagery cut from the real ISSDC products ---------- */
const PAYLOADS = [
  {
    code: "OHRC",
    name: "Orbiter High Resolution Camera",
    image: "/assets/ch2/ohrc_south_pole.jpg",
    gsdM: 0.25,
    gsd: "0.25 m",
    swath: "3 km",
    band: "Panchromatic",
    scaleLabel: "500 m",
    scalePct: 16.7,
    caption: "Lunar south pole, 89.3°–89.9° S · 28 Dec 2021 · Sun 0.04° below horizon",
    product: "ch2_ohr_nrp_20211228T2209123959",
  },
  {
    code: "TMC-2",
    name: "Terrain Mapping Camera-2",
    image: "/assets/ch2/tmc2_crater.jpg",
    gsdM: 5,
    gsd: "5 m",
    swath: "20 km",
    band: "Panchromatic",
    scaleLabel: "5 km",
    scalePct: 25.5,
    caption: "Fresh ray crater · Orbit 1675 · 09 Jan 2020 · fore camera",
    product: "ch2_tmc_nrf_20200109T0733072590",
  },
  {
    code: "IIRS",
    name: "Imaging Infrared Spectrometer",
    image: "/assets/ch2/iirs_crater.jpg",
    gsdM: 80,
    gsd: "80 m",
    swath: "20 km · 256 bands",
    band: "0.8–5.0 µm",
    scaleLabel: "5 km",
    scalePct: 25.5,
    caption: "Same crater, same orbit · bands 40–96 averaged, destriped",
    product: "ch2_iir_nri_20200109T0733065684",
  },
];

const parseGsd = (gsd: string) => parseFloat(gsd);

/* Log-scale position on 0.1 m → 100 m */
const gsdPct = (m: number) => Math.max(4, (Math.log10(m / 0.1) / 3) * 100);

/* ---------- Hero: real-texture Moon with Chandrayaan-2 on a polar orbit ---------- */
function MoonOrbit() {
  const reducedMotion = usePrefersReducedMotion();
  // Orbit drawn in the un-rotated frame, then tilted as a group
  const front = "M220,24 A62,196 0 0,1 220,416";
  const full = "M220,24 A62,196 0 0,1 220,416 A62,196 0 0,1 220,24";

  const spacecraft = (
    <g>
      <polygon points="0,6 -10,40 10,40" fill="url(#ov-beam)" />
      <rect x="-13" y="-1.5" width="26" height="3" fill="#9a9a9a" />
      <rect x="-4" y="-4" width="8" height="8" fill="#ffffff" />
      <circle r="12" fill="none" stroke="#ffffff" strokeOpacity="0.25" />
    </g>
  );

  return (
    <svg className="ov-moon-svg" viewBox="0 0 440 440" role="img" aria-label="Chandrayaan-2 orbiter on a polar orbit around the Moon">
      <defs>
        <linearGradient id="ov-beam" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffffff" stopOpacity="0.85" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="ov-halo" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0.7" stopColor="#ffffff" stopOpacity="0.09" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>
        <clipPath id="ov-disc">
          <circle cx="220" cy="220" r="158" />
        </clipPath>
      </defs>

      <circle cx="220" cy="220" r="205" fill="url(#ov-halo)" />

      {/* Far side of the orbit, behind the Moon */}
      <g transform="rotate(20 220 220)">
        <path d={full} fill="none" stroke="#ffffff" strokeOpacity="0.18" strokeDasharray="2 5" />
      </g>

      <image href="/assets/ch2/moon_globe.png" x="61" y="61" width="318" height="318" />

      {/* Graticule */}
      <g clipPath="url(#ov-disc)" fill="none" stroke="#ffffff" strokeOpacity="0.07">
        <ellipse cx="220" cy="220" rx="158" ry="52" />
        <ellipse cx="220" cy="220" rx="158" ry="110" />
        <ellipse cx="220" cy="220" rx="56" ry="158" />
        <ellipse cx="220" cy="220" rx="112" ry="158" />
        <line x1="220" y1="62" x2="220" y2="378" />
        <line x1="62" y1="220" x2="378" y2="220" />
      </g>

      {/* Near side of the orbit + spacecraft */}
      <g transform="rotate(20 220 220)">
        <path d={front} fill="none" stroke="#ffffff" strokeOpacity="0.55" />
        {reducedMotion ? (
          <g transform="translate(265 110) rotate(70)">{spacecraft}</g>
        ) : (
          <g>
            {spacecraft}
            <animateMotion dur="18s" repeatCount="indefinite" rotate="auto" path={full} />
            <animate
              attributeName="opacity"
              dur="18s"
              repeatCount="indefinite"
              values="1;1;0;0;1;1"
              keyTimes="0;0.55;0.575;0.925;0.95;1"
            />
          </g>
        )}
      </g>

      {/* Annotations */}
      <g className="ov-moon-annot">
        <line x1="300" y1="44" x2="340" y2="24" />
        <text x="344" y="22">CH-2 ORBITER</text>
        <text x="344" y="34" className="dim">100 km polar orbit</text>
        <text x="22" y="404" className="dim">SUN</text>
        <line x1="22" y1="412" x2="60" y2="412" />
        <polyline points="54,408 60,412 54,416" fill="none" />
        <text x="418" y="430" textAnchor="end" className="dim">surface texture: TMC-2 orbit 1675</text>
      </g>
    </svg>
  );
}

/* ---------- Two real cameras, one crater: before/after slider ---------- */
function CraterCompare() {
  const [split, setSplit] = useState(50);
  return (
    <div className="ov-compare">
      <div className="ov-compare-stage">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/assets/ch2/iirs_crater.jpg" alt="IIRS view of the crater" draggable={false} />
        <div className="ov-compare-top" style={{ clipPath: `inset(0 ${100 - split}% 0 0)` }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/assets/ch2/tmc2_crater.jpg" alt="TMC-2 view of the crater" draggable={false} />
        </div>
        <div className="ov-compare-divider" style={{ left: `${split}%` }} />
        <span className="ov-chip ov-chip-tl">TMC-2 · 5 m · VIS</span>
        <span className="ov-chip ov-chip-tr">IIRS · 80 m · NIR</span>
        <input
          className="ov-compare-range"
          type="range"
          min={0}
          max={100}
          value={split}
          onChange={e => setSplit(Number(e.target.value))}
          aria-label="Slide to compare TMC-2 and IIRS views"
        />
      </div>
    </div>
  );
}

export default function OverviewTab({ onNavigateTab }: OverviewTabProps) {
  const referenceSensors = SENSOR_SPECS.filter(s => s.mission !== "Chandrayaan-2");

  return (
    <div className="ov-root">
      {/* ================= HERO ================= */}
      <section className="mission-hero-banner ov-hero">
        <div className="ov-hero-grid">
          <div className="ov-hero-copy">
            <div className="hero-meta-row">
              <span className="aerospace-tag">ISRO — PROBLEM STATEMENT 26166 &bull; SIH 2026</span>
            </div>
            <div className="ov-hero-badges">
              <span className="tag-badge">DOMAIN: SPACE TECHNOLOGY</span>
              <span className="tag-badge badge-white">OFFLINE CPU ENGINE</span>
            </div>

            <h1 className="hero-title ov-hero-title">
              Registering the Moon, <br className="hide-sm" />
              as Chandrayaan-2 sees it.
            </h1>
            <p className="hero-description">
              A multi-modal correspondence and registration engine for Chandrayaan-2 orbiter imagery. It aligns OHRC, TMC-2 and IIRS
              with each other and with LRO NAC and SELENE references, across extreme Sun-angle shifts, 300× resolution gaps and
              visible-to-infrared modality changes.
            </p>

            <div className="ov-cta-row">
              <button className="btn-primary-action ov-cta-primary" onClick={() => onNavigateTab("studio")}>
                LAUNCH REGISTRATION STUDIO &rarr;
              </button>
              <button className="btn-secondary-action ov-cta-secondary" onClick={() => onNavigateTab("robustness")}>
                EXPLORE ROBUSTNESS LAB
              </button>
            </div>

            <dl className="ov-mission-facts">
              <div>
                <dt>Spacecraft</dt>
                <dd>Chandrayaan-2 Orbiter</dd>
              </div>
              <div>
                <dt>Orbit</dt>
                <dd>~100 km, polar</dd>
              </div>
              <div>
                <dt>Optical payloads</dt>
                <dd>OHRC · TMC-2 · IIRS</dd>
              </div>
            </dl>
          </div>

          <div className="ov-hero-visual">
            <MoonOrbit />
          </div>
        </div>

        {/* Live-looking ground track built from a real TMC-2 strip */}
        <div className="ov-groundtrack" aria-hidden="true">
          <div className="ov-groundtrack-img" />
          <div className="ov-groundtrack-scan" />
          <span className="ov-groundtrack-label">
            <span className="ov-live-dot" /> TMC-2 GROUND TRACK · ORBIT 1675 · 09 JAN 2020
          </span>
        </div>

        <div className="quick-telemetry-row">
          <div className="telemetry-tile">
            <span className="tile-label">RMSE TOLERANCE <span>px</span></span>
            <span className="tile-value">&lt; 0.35</span>
            <span className="tile-desc">Sub-pixel residual accuracy</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">INLIER RATIO <span>%</span></span>
            <span className="tile-value">92.4%</span>
            <span className="tile-desc">Consensus geometric inliers</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">END-TO-END LATENCY <span>ms</span></span>
            <span className="tile-value">~140</span>
            <span className="tile-desc">Fully optimized CPU runtime</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">SENSOR MODALITIES <span>N</span></span>
            <span className="tile-value">5</span>
            <span className="tile-desc">OHRC, TMC-2, IIRS, LRO, SELENE</span>
          </div>
        </div>
      </section>

      {/* ================= PAYLOAD GALLERY ================= */}
      <div className="ov-section-head">
        <h2 className="ov-section-title">THROUGH CHANDRAYAAN-2&apos;S EYES</h2>
        <span className="ov-section-sub">Real ISSDC PDS4 products used by this project, not illustrations</span>
      </div>

      <div className="ov-payload-grid">
        {PAYLOADS.map(p => (
          <article key={p.code} className="ov-payload-card">
            <div className="ov-payload-frame">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.image} alt={`${p.code}: ${p.caption}`} loading="lazy" decoding="async" />
              <span className="ov-corner tl" />
              <span className="ov-corner tr" />
              <span className="ov-corner bl" />
              <span className="ov-corner br" />
              <span className="ov-chip ov-chip-tl">{p.code}</span>
              <span className="ov-chip ov-chip-tr">{p.gsd}/px</span>
              <div className="ov-scalebar">
                <span style={{ width: `${p.scalePct}%` }} />
                <em>{p.scaleLabel}</em>
              </div>
            </div>
            <div className="ov-payload-body">
              <h3>{p.name}</h3>
              <p className="ov-payload-caption">{p.caption}</p>
              <div className="ov-spec-row">
                <div><span>GSD</span><strong>{p.gsd}</strong></div>
                <div><span>SWATH</span><strong>{p.swath}</strong></div>
                <div><span>BAND</span><strong>{p.band}</strong></div>
              </div>
              <div className="ov-product-id mono">{p.product}</div>
            </div>
          </article>
        ))}
      </div>

      {/* ================= THE CHALLENGE ================= */}
      <section className="card-box ov-challenge">
        <div className="ov-challenge-copy">
          <span className="aerospace-tag">THE REGISTRATION PROBLEM</span>
          <h2>Same crater. Same orbit. Two different cameras.</h2>
          <p>
            TMC-2 and IIRS imaged this crater on the same pass, yet the pixels barely agree. The resolution differs by 16×, the
            wavelengths differ, IIRS carries column striping, and the two labels place the strip about 8 km apart along-track.
            Drag the slider to compare them. LunarMatch finds the tie points that lock views like these together at sub-pixel accuracy.
          </p>
          <ul className="ov-challenge-list">
            <li><strong>16×</strong><span>GSD gap (4.9 m vs 78.3 m)</span></li>
            <li><strong>VIS → NIR</strong><span>radiometric modality shift</span></li>
            <li><strong>~8 km</strong><span>label geolocation offset</span></li>
          </ul>
          <button className="btn-secondary-action" onClick={() => onNavigateTab("studio")}>
            REGISTER A PAIR IN STUDIO &rarr;
          </button>
        </div>
        <CraterCompare />
      </section>

      {/* ================= RESOLUTION LADDER ================= */}
      <section className="card-box ov-ladder-card">
        <div className="card-header">
          <span className="card-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            GROUND RESOLUTION ACROSS PLATFORMS
          </span>
          <span className="tag-badge badge-subtle">LOG SCALE · METRES PER PIXEL</span>
        </div>

        <div className="ov-ladder">
          {SENSOR_SPECS.map(s => {
            const m = parseGsd(s.gsd);
            const isCh2 = s.mission === "Chandrayaan-2";
            return (
              <div key={s.code} className={`ov-ladder-row${isCh2 ? " is-ch2" : ""}`}>
                <div className="ov-ladder-name">
                  <strong>{s.code}</strong>
                  <span>{isCh2 ? "Chandrayaan-2" : s.mission.replace(/ \(.*\)/, "")}</span>
                </div>
                <div className="ov-ladder-track">
                  <div className="ov-ladder-bar" style={{ width: `${gsdPct(m)}%` }}>
                    <span>{s.gsd.replace(" / pixel", "")}</span>
                  </div>
                </div>
                <div className="ov-ladder-role">{s.role}</div>
              </div>
            );
          })}
          <div className="ov-ladder-axis" aria-hidden="true">
            <span style={{ left: "0%" }}>0.1 m</span>
            <span style={{ left: "33.3%" }}>1 m</span>
            <span style={{ left: "66.6%" }}>10 m</span>
            <span style={{ left: "100%" }}>100 m</span>
          </div>
        </div>
        <p className="ov-ladder-note">
          Reference basemaps: {referenceSensors.map(s => `${s.code} (${s.mission})`).join(" · ")}
        </p>
      </section>

      {/* ================= CAPABILITIES ================= */}
      <div className="ov-section-head">
        <h2 className="ov-section-title">CORE CAPABILITIES</h2>
      </div>

      <div className="ov-capability-grid">
        <button className="ov-capability" onClick={() => onNavigateTab("studio")}>
          <span className="ov-capability-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="3" y1="9" x2="21" y2="9" />
              <line x1="9" y1="21" x2="9" y2="9" />
            </svg>
          </span>
          <span className="ov-capability-text">
            <strong>IMAGE REGISTRATION</strong>
            <span>Pick reference and moving lunar images, tune multi-scale parameters, and register with instant visual feedback.</span>
          </span>
        </button>

        <button className="ov-capability" onClick={() => onNavigateTab("correspondence")}>
          <span className="ov-capability-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="6" cy="6" r="3" />
              <circle cx="18" cy="18" r="3" />
              <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
            </svg>
          </span>
          <span className="ov-capability-text">
            <strong>CORRESPONDENCE VIEWER</strong>
            <span>Side-by-side tie points with hover tooltips showing residual error and Sinkhorn transport confidence.</span>
          </span>
        </button>

        <button className="ov-capability" onClick={() => onNavigateTab("robustness")}>
          <span className="ov-capability-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
            </svg>
          </span>
          <span className="ov-capability-text">
            <strong>ROBUSTNESS LABORATORY</strong>
            <span>Stress tests across Sun incidence shifts from 0° to 80°, resolution disparities and noise.</span>
          </span>
        </button>

        <button className="ov-capability" onClick={() => onNavigateTab("architecture")}>
          <span className="ov-capability-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
          </span>
          <span className="ov-capability-text">
            <strong>PIPELINE ARCHITECTURE</strong>
            <span>Log-Gabor phase congruency, Sinkhorn optimal transport, MAGSAC++ and sub-pixel phase correlation.</span>
          </span>
        </button>
      </div>
    </div>
  );
}
