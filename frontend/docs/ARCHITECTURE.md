# LunarMatch — React + Vite Frontend Architecture

> **Design source of truth:** `stitch_lunarmatch_frontend_application/` HTML prototypes + `orbital_aerospace_monochrome/DESIGN.md`  
> **Backend:** FastAPI at `http://10.0.2.2:8000` (dev: `http://localhost:8000`)  
> **Target:** Production-grade SPA — mission-control workstation for ISRO SIH 2026

---

## Stack

| Layer | Technology | Version |
|---|---|---|
| Build | Vite | 6.x |
| UI | React | 19.x |
| Routing | React Router | 7.x |
| Styling | Tailwind CSS | 4.x |
| Animation | Framer Motion + GSAP | 12.x / 3.x |
| Server state | TanStack Query | 5.x |
| Client state | Zustand | 5.x |
| HTTP | Axios | 1.x |
| Charts | Inline SVG (React) | — |
| Icons | Material Symbols Outlined | variable font |
| Fonts | Google Fonts CDN | — |

---

## Project Structure

```
lunarmatch-web/
├── public/
│   └── favicon.svg                          # Radar icon SVG
│
├── index.html                               # <html class="dark"> — Google Fonts + Material Symbols <link>s
│
├── src/
│   ├── main.jsx                             # Vite entry — QueryClient + ZustandProvider + <App>
│   ├── App.jsx                              # <RouterProvider> with root layout
│   │
│   ├── router/
│   │   └── index.jsx                        # createBrowserRouter — 5 lazy routes + AppShell layout
│   │
│   ├── shell/                               # Shared chrome present on every page
│   │   ├── AppShell.jsx                     # <aside> + <header> + <Outlet> compositional wrapper
│   │   ├── Sidebar.jsx                      # Fixed w-72 sidebar: logo, nav, node-status, user row
│   │   ├── SidebarNavItem.jsx               # Single animated nav link — Framer Motion whileHover/layout
│   │   ├── TopHeader.jsx                    # h-16 fixed bar: breadcrumb, UTC clock, API chip, Raw Logs
│   │   └── hooks/
│   │       ├── useUtcClock.js               # setInterval → live UTC string (updates every 100ms for sub-second display)
│   │       └── useApiStatus.js              # TanStack Query polling /health every 30s → online/offline chip
│   │
│   ├── pages/
│   │   │
│   │   ├── Dashboard/
│   │   │   ├── Dashboard.jsx                # Root: mission banner + KPI grid + 7/12–5/12 columns
│   │   │   ├── MissionBanner.jsx            # Full-width hero — GSAP staggered entrance on mount
│   │   │   ├── KpiGrid.jsx                  # 4-up metric cards — Framer Motion stagger container
│   │   │   ├── StudioPreview.jsx            # Module 01 — image pair preview + HomographySvgChart
│   │   │   ├── RobustnessPreview.jsx        # Module 02 — 4 DoF stat chips + SVG robustness curve
│   │   │   ├── ArchitectureSummary.jsx      # Module 03 — 3 grouped pipeline stage cards
│   │   │   ├── QuickRunPanel.jsx            # Module 04 — region selector, config grid, run CTA
│   │   │   ├── TelemetryJobs.jsx            # Module 05 — inlier pairs list with status badges
│   │   │   └── hooks/
│   │   │       └── useDashboardData.js      # TanStack Query: /api/v1/capabilities + pipeline status
│   │   │
│   │   ├── Registration/
│   │   │   ├── Registration.jsx             # Step header + info banner + dual column + algo config + action bar
│   │   │   ├── StepHeader.jsx               # "STEP 01 OF 04" row + Swap / Clear / Load Sample buttons
│   │   │   ├── InfoBanner.jsx               # Reference vs Moving concept explainer card
│   │   │   ├── ImagePanel.jsx               # Reusable panel: badge, sensor selects, viewport, stats, histogram, dropzone
│   │   │   ├── AlgorithmConfig.jsx          # Feature engine pills + geometric model pills + grid params
│   │   │   ├── ActionBar.jsx                # Sticky bottom: readiness dot + Preview + Continue CTA
│   │   │   └── hooks/
│   │   │       └── useRegistration.js       # Zustand-backed: images, engine, model, isSwapped
│   │   │
│   │   ├── RobustnessLab/
│   │   │   ├── RobustnessLab.jsx            # Page: section header + 3-column (4/4/4) workstation
│   │   │   ├── PerturbationSetup.jsx        # 4-DoF selector + step granularity + engine options + presets + run CTA
│   │   │   ├── DegradationChart.jsx         # Inline SVG curve + interactive anchor points + telemetry matrix table + verdict banner
│   │   │   ├── OpticalInspection.jsx        # Dual viewport (T_0/T_MAX) + heatmap + export / log buttons
│   │   │   └── hooks/
│   │   │       └── useRobustnessLab.js      # Local: selectedParam, selectedStep, sweepLoading
│   │   │
│   │   ├── Capabilities/
│   │   │   ├── Capabilities.jsx             # Page: banner + 7/12 pipeline + 5/12 sidebar
│   │   │   ├── PipelineStageCard.jsx        # Stage: number badge + title + description + tech tags + connector arrow
│   │   │   ├── ApiInterface.jsx             # Endpoint input + ping button + latency/FPS gauges
│   │   │   ├── MissionSpec.jsx              # 2×2 mission metadata grid
│   │   │   ├── EngineCapabilityCard.jsx     # Capability: title + version badge + description + param row
│   │   │   ├── ConsoleStream.jsx            # Monospace boot-log output panel — GSAP typewriter on mount
│   │   │   └── hooks/
│   │   │       └── useApiPing.js            # performance.now() ping → measured latency
│   │   │
│   │   └── MissionInfo/
│   │       └── MissionInfo.jsx              # 5th nav route — mission telemetry info (mirrors banner pattern)
│   │
│   ├── components/                          # Domain-agnostic primitives — pure presentational
│   │   │
│   │   ├── ui/
│   │   │   ├── Badge.jsx                    # variant: 'code' | 'status' | 'version'
│   │   │   ├── Button.jsx                   # variant: 'primary' | 'ghost' | 'icon' + loading state
│   │   │   ├── Chip.jsx                     # Selectable pill — Framer Motion layout animation on active swap
│   │   │   ├── Icon.jsx                     # <span class="material-symbols-outlined"> wrapper w/ size prop
│   │   │   ├── MetricCard.jsx               # label + big value + unit + subline — Framer Motion count-up
│   │   │   ├── SectionHeader.jsx            # icon box + uppercase title + right meta text
│   │   │   ├── StatusDot.jsx                # pulse / solid dot with label (online/offline/pending)
│   │   │   ├── TechTag.jsx                  # Dark pill for stage tech specs (e.g. "Log-Gabor Bank 4×6")
│   │   │   └── TelemetryRow.jsx             # Table row: pair ID + inlier count + RMSE + status badge
│   │   │
│   │   ├── charts/
│   │   │   ├── DegradationSvgChart.jsx      # SVG degradation curve — GSAP DrawSVG path reveal on enter
│   │   │   └── HomographySvgChart.jsx       # SVG convergence line chart — GSAP DrawSVG on mount
│   │   │
│   │   └── ImageViewport.jsx                # Image well: src, overlay badges, crosshair, coordinate readout
│   │
│   ├── data/                                # Static constants — drives data-in, UI-out rendering
│   │   ├── navItems.js                      # NAV_ITEMS array: path, icon, codeLabel, name
│   │   ├── pipelineStages.js                # PIPELINE_STAGES[9]: id, title, description, tags[], icon
│   │   └── engineCapabilities.js            # ENGINE_CAPABILITIES[7]: id, title, version, description, params[]
│   │
│   ├── services/
│   │   ├── api.js                           # axios.create — baseURL from VITE_API_BASE_URL
│   │   ├── pipelineApi.js                   # runPipeline(params), getPipelineStatus(jobId)
│   │   ├── capabilitiesApi.js               # getCapabilities()
│   │   └── healthApi.js                     # ping() → { latency_ms }
│   │
│   ├── store/
│   │   └── registrationStore.js             # Zustand: referenceFile, movingFile, selectedEngine, selectedModel
│   │
│   └── styles/
│       ├── index.css                        # @import "tailwindcss"; scrollbar suppression; base resets
│       └── fonts.css                        # @import for Space Grotesk, Inter, JetBrains Mono, Material Symbols
│
├── tailwind.config.js                       # Full Orbital Aerospace Monochrome design token set
├── vite.config.js                           # Path alias @/ → src/, port 3000
├── .env.development                         # VITE_API_BASE_URL=http://localhost:8000
└── .env.production                          # VITE_API_BASE_URL=http://10.0.2.2:8000
```

---

## Routing

React Router v7 `createBrowserRouter`. All routes are **lazily loaded** — initial bundle contains only the shell.

```
/                   →  Dashboard           (01 // CORE)
/registration       →  Registration        (02 // PIPELINE)
/robustness-lab     →  RobustnessLab       (03 // STRESS-TEST)
/capabilities       →  Capabilities        (04 // ENGINE SPEC)
/mission-info       →  MissionInfo         (05 // TELEMETRY)
```

`AppShell` is the root layout wrapper — sidebar + header render unconditionally, `<Outlet>` renders the matched page. Page transitions are animated by Framer Motion `<AnimatePresence>` wrapping `<Outlet>`.

Active nav link detection: `useMatch(item.path)` inside `SidebarNavItem`. Active classes: `bg-surface-container-high text-primary font-bold`. `aria-current="page"` set programmatically.

---

## Shell Architecture

### `AppShell`
- `<aside>` fixed `left-0 top-0 h-full w-72 z-50 bg-surface-container-lowest`
- `<header>` fixed `top-0 left-72 right-0 h-16 z-40 bg-surface-container-lowest/90 backdrop-blur-md`
- `<main>` `pl-72 pt-16 bg-surface min-h-screen`
- Breadcrumb text provided to header via `BreadcrumbContext` — each page sets it with `useBreadcrumb()` inside a `useEffect`

### `Sidebar`
Three stacked sections (`justify-between` flex column):
1. **Top** — Logo (radar icon + "LunarMatch" + version badge) + nav section label + 5 `<SidebarNavItem>` components
2. **Bottom** — NodeStatus panel (LATENCY + OHRC/TMC-2/IIRS chips) + UserRow (avatar + name + power icon)

`SidebarNavItem` uses Framer Motion `whileHover={{ x: 2 }}` for a subtle rightward nudge on hover, and `layout` prop so the active highlight capsule morphs smoothly when navigating.

### `TopHeader`
- Left: breadcrumb (`WORKSPACE › <PAGE_NAME>`) + crater coord pill (hidden `< xl`)
- Right: UTC clock pill → `useUtcClock()` updates every 100ms for `.xx` sub-second display; FastAPI chip → `useApiStatus()`; Raw Logs button; avatar circle

---

## Animation Strategy

Framer Motion and GSAP serve distinct roles — chosen per use-case, never mixed for the same element.

### Framer Motion — React-driven, declarative

Used for: component mount/unmount, layout shifts, interactive micro-interactions, staggered list entrances.

| Location | Animation |
|---|---|
| `<AnimatePresence>` on `<Outlet>` | Page transition: `opacity 0→1`, `y 8→0`, 200ms ease-out |
| `KpiGrid` children | `staggerChildren: 0.05` — cards fade+slide up sequentially on mount |
| `SidebarNavItem` | `whileHover={{ x: 2 }}` subtle translate; `layout` for active capsule morph |
| `Chip` (algorithm pills) | `layout` — active indicator slides between pills without hard jump |
| `MetricCard` value | Count-up effect via `useSpring` + `useTransform` on entry |
| `Button` (primary) | `whileTap={{ scale: 0.98 }}` — replaces CSS `active:scale-[0.98]` |
| `QuickRunPanel` CTA | Loading state: inner icon `animate={{ rotate: 360 }}` continuous spin |
| `PerturbationSetup` param rows | `AnimatePresence` + height collapse on param switching |
| `StatusDot` (pulse variant) | `animate={{ scale: [1, 1.4, 1] }}` repeating pulse (replaces CSS `animate-pulse`) |

### GSAP — imperative, timeline-based, SVG

Used for: complex SVG path reveals, typewriter effects, scroll-triggered sequences that need precise timing control.

| Location | Plugin | Animation |
|---|---|---|
| `DegradationSvgChart` — path reveal | `DrawSVGPlugin` | Stroke draws from 0% to 100% on component entry (1.0s ease-out) |
| `HomographySvgChart` — convergence line | `DrawSVGPlugin` | Same stroke-draw entrance, 0.8s, triggered by `IntersectionObserver` |
| `MissionBanner` — H1 + description | `gsap.from()` stagger | Words slide up with `y: 20, opacity: 0`, `stagger: 0.03` |
| `ConsoleStream` — boot log lines | `gsap.to()` timeline | Lines appear one-by-one with 80ms gap — typewriter without plugins |
| `OpticalInspection` — heatmap overlay | `gsap.fromTo()` | Overlay fades in, contour badges slide from edges |
| `RobustnessLab` — table rows on step select | `gsap.to()` | Highlighted row background flashes (flash then settles) |

GSAP instances are created inside `useEffect` with a cleanup `ctx.revert()` — no memory leaks on unmount. All GSAP animations reference DOM elements via `useRef` — never string selectors.

### When neither is used
Static hover/focus states (`transition-colors`, `transition-all`) remain as Tailwind utilities — no library overhead for simple color transitions.

---

## State Management

| Concern | Tool | Why |
|---|---|---|
| Algorithm config + image pair (persists across routes) | **Zustand** `registrationStore` | Survives navigation; user configures on `/registration`, submits from `/` QuickRunPanel |
| UI toggles: active pill, selected step, sweep loading | **`useState`** local in page hooks | Never shared — co-located with the component that owns it |
| Server data: capabilities, pipeline status, health | **TanStack Query** | Automatic caching, background refetch, loading/error states |
| Active route + breadcrumb label | **React Router** `useMatch` + **React Context** `BreadcrumbContext` | Sidebar reads route; pages write breadcrumb text |
| UTC clock string | **`useUtcClock` hook** | `setInterval` → `useState`, cleaned up on unmount |
| FastAPI health status | **TanStack Query** `refetchInterval: 30_000` | Non-blocking; shows stale indicator chip on offline |

---

## API Service Layer

All API calls go through TanStack Query hooks in `src/services/`. No raw `fetch`/`axios` in components.

```
src/services/
  api.js               →  axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL })
  pipelineApi.js       →  runPipeline(params)  ·  getPipelineStatus(jobId)
  capabilitiesApi.js   →  getCapabilities()
  healthApi.js         →  ping()  →  { latency_ms, version }
```

Hook layer (co-located in each page's `hooks/` directory):
```
useDashboardData()     →  useQuery(['capabilities'])  +  useQuery(['pipeline-status'])
useRegistration()      →  local state  +  useMutation(['pipeline-run'])
useRobustnessLab()     →  local state  +  useMutation(['sweep-run'])
useApiPing()           →  manual fetch on button click → performance.now() delta
useApiStatus()         →  useQuery(['health'], { refetchInterval: 30_000 })
```

---

## Tailwind Design Token Config

The `tailwind.config.js` migrates the inline config verbatim from the HTML prototypes.

### Color Tokens (exact hex values)
```js
colors: {
  // Surface elevation (darkest to lightest)
  'surface-container-lowest':  '#0e0e0e',
  'surface-container-low':     '#1b1b1b',
  'surface-container':         '#1f1f1f',
  'surface-container-high':    '#2a2a2a',
  'surface-container-highest': '#353535',
  'surface':                   '#131313',
  'surface-variant':           '#353535',
  'surface-bright':            '#393939',

  // On-surface text
  'on-surface':                '#e2e2e2',
  'on-surface-variant':        '#c4c7c8',
  'on-background':             '#e2e2e2',
  'background':                '#131313',

  // Primary — white only
  'primary':                   '#ffffff',
  'on-primary':                '#2f3131',
  'primary-container':         '#e2e2e2',
  'primary-fixed':             '#e2e2e2',
  'primary-fixed-dim':         '#c6c6c7',

  // Borders & outlines
  'outline':                   '#8e9192',
  'outline-variant':           '#444748',

  // Error states
  'error':                     '#ffb4ab',
  'error-container':           '#93000a',
  'on-error':                  '#690005',
  'on-error-container':        '#ffdad6',

  // Secondary / tertiary (muted)
  'secondary':                 '#c8c6c5',
  'secondary-container':       '#474746',
  'tertiary':                  '#ffffff',
}
```

### Typography Tokens
```js
fontFamily: {
  'headline-lg':  ['Space Grotesk'],   // 20px / 700 / tracking 0.08em
  'headline-md':  ['Space Grotesk'],   // 16px / 700 / tracking 0.06em
  'headline-sm':  ['Inter'],           // 14px / 600 / tracking 0.02em
  'body-lg':      ['Inter'],           // 14px / 400
  'body-md':      ['Inter'],           // 12px / 400
  'label-lg':     ['Space Grotesk'],   // 12px / 700 / tracking 0.08em
  'label-md':     ['JetBrains Mono'],  // 11px / 500 / tracking 0.04em
  'label-sm':     ['JetBrains Mono'],  // 10px / 500 / tracking 0.02em
}
fontSize: {
  'headline-lg': ['20px', { lineHeight: '24px', letterSpacing: '0.08em', fontWeight: '700' }],
  'headline-md': ['16px', { lineHeight: '20px', letterSpacing: '0.06em', fontWeight: '700' }],
  'headline-sm': ['14px', { lineHeight: '18px', letterSpacing: '0.02em', fontWeight: '600' }],
  'body-lg':     ['14px', { lineHeight: '20px', fontWeight: '400' }],
  'body-md':     ['12px', { lineHeight: '17px', fontWeight: '400' }],
  'label-lg':    ['12px', { lineHeight: '16px', letterSpacing: '0.08em', fontWeight: '700' }],
  'label-md':    ['11px', { lineHeight: '14px', letterSpacing: '0.04em', fontWeight: '500' }],
  'label-sm':    ['10px', { lineHeight: '12px', letterSpacing: '0.02em', fontWeight: '500' }],
}
```

### Spacing & Shape Tokens
```js
borderRadius: {
  DEFAULT: '0.25rem',   // rounded
  lg:      '0.5rem',    // rounded-lg
  xl:      '0.75rem',   // rounded-xl  ← primary card radius
  full:    '9999px',    // rounded-full ← pill buttons
},
spacing: {
  'space-xs': '0.25rem',
  'space-sm': '0.5rem',
  'space-md': '0.75rem',
  'space-lg': '1rem',      // primary card padding
  'space-xl': '1.25rem',
  'gutter':   '0.75rem',
  'margin':   '1rem',
},
```

---

## Component Primitive Inventory

All primitives are purely presentational — zero business logic, typed props.

| Component | Key Props | Animation | Used In |
|---|---|---|---|
| `Badge` | `label`, `variant: 'code'\|'status'\|'version'` | — | Every page |
| `Button` | `variant: 'primary'\|'ghost'\|'icon'`, `loading`, `onClick` | `whileTap={{ scale: 0.98 }}` (FM) | All CTAs |
| `Chip` | `label`, `active`, `onClick` | `layout` morph (FM) | Algorithm config, granularity selector |
| `Icon` | `name`, `size` | — | Everywhere |
| `MetricCard` | `label`, `value`, `unit`, `subValue` | Count-up via `useSpring` (FM) | Dashboard KPIs, Robustness ribbon |
| `SectionHeader` | `icon`, `title`, `meta` | — | Module headers |
| `StatusDot` | `status: 'online'\|'pulse'\|'offline'`, `label` | Scale pulse (FM) | Header, sidebar, dashboard |
| `TechTag` | `label` | — | Pipeline stages, capability cards |
| `TelemetryRow` | `id`, `inliers`, `rmse`, `status` | — | Dashboard, Robustness table |
| `PipelineStageCard` | `stageId`, `title`, `description`, `tags[]`, `icon` | Hover `bg` transition (CSS) | Dashboard + Capabilities |
| `ImageViewport` | `src`, `alt`, `badge`, `overlays[]` | — | Registration, Robustness |
| `DegradationSvgChart` | `steps[]`, `selectedStep`, `onSelectStep` | DrawSVG path reveal (GSAP) | Robustness Lab |
| `HomographySvgChart` | `data[]` | DrawSVG on mount (GSAP) | Dashboard Studio Preview |

---

## Page Layout Reference

### Dashboard `/`
```
<MissionBanner />                          ← full-width GSAP entrance
<KpiGrid />                                ← 4-col FM stagger

<div class="grid lg:grid-cols-12 gap-space-lg">
  <div class="lg:col-span-7">
    <StudioPreview />                      ← Module 01
    <RobustnessPreview />                  ← Module 02
    <ArchitectureSummary />               ← Module 03
  </div>
  <div class="lg:col-span-5">
    <QuickRunPanel />                      ← Module 04
    <TelemetryJobs />                      ← Module 05
  </div>
</div>
```

### Registration `/registration`
```
<StepHeader />                             ← "STEP 01 OF 04" + action buttons
<InfoBanner />                             ← Reference vs Moving explainer
<div class="xl:grid-cols-2">
  <ImagePanel role="reference" />          ← Frame A // Fixed
  <ImagePanel role="moving" />             ← Frame B // Target (Warped)
</div>
<AlgorithmConfig />                        ← Engine pills + model pills + grid params
<ActionBar />                              ← Readiness indicator + CTAs
```

### Robustness Lab `/robustness-lab`
```
<SectionBanner />                          ← "LAB-EXP // 03-SWEEP" + telemetry ribbon

<div class="lg:grid-cols-12">
  <div class="lg:col-span-4">
    <PerturbationSetup />                  ← 4-DoF + presets + Run CTA
  </div>
  <div class="lg:col-span-4">
    <DegradationChart />                   ← SVG + telemetry table + verdict
  </div>
  <div class="lg:col-span-4">
    <OpticalInspection />                  ← Dual viewport + heatmap + export
  </div>
</div>
```

### Capabilities `/capabilities`
```
<SectionBanner />                          ← "SPEC // SYS-DOC-26166" + H1

<div class="xl:grid-cols-12">
  <div class="xl:col-span-7">
    {PIPELINE_STAGES.map(stage =>          ← 9 data-driven stage cards
      <PipelineStageCard /> + <ConnectorArrow />
    )}
  </div>
  <div class="xl:col-span-5">
    <ApiInterface />                       ← endpoint + ping + gauges
    <MissionSpec />                        ← 2×2 metadata grid
    {ENGINE_CAPABILITIES.map(cap =>        ← 7 data-driven capability cards
      <EngineCapabilityCard />
    )}
    <ConsoleStream />                      ← GSAP typewriter boot log
  </div>
</div>
```

---

## SVG Charts

Both charts use **inline React SVG** — no charting library. This matches the designs exactly and allows GSAP `DrawSVGPlugin` to animate the `stroke-dashoffset` on mount.

**`DegradationSvgChart`** — `viewBox="0 0 400 180"`:
- Background grid lines (dashed, `#353535`)
- 50% threshold boundary line
- Inlier area fill with `linearGradient`
- Inlier line path + RMSE dashed path
- 5 interactive anchor points — React `onClick` → `onSelectStep(i)`
- x-axis delta labels in JetBrains Mono

**`HomographySvgChart`** — convergence line with gradient fill, no interactive points.

GSAP integration pattern:
```jsx
const pathRef = useRef(null);
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.from(pathRef.current, {
      drawSVG: '0%',
      duration: 1.0,
      ease: 'power2.out',
    });
  });
  return () => ctx.revert();
}, []);
```

---

## Error Handling

- **Error Boundaries** — one per page-level route. Fallback renders an aerospace-style card:  
  `"TELEMETRY LINK LOST // SUBSYSTEM FAULT"` in the design system — `bg-surface-container-lowest`, `text-primary`, JetBrains Mono readout with the error message.
- **API errors** — TanStack Query `isError` state surfaces an inline `StatusDot status="offline"` chip in the relevant component. No full-page crashes.
- **Image load failures** — `ImageViewport` renders a `bg-surface-container-lowest` placeholder with `filter_center_focus` icon and "NO TELEMETRY FEED" label.

---

## Performance

- **Lazy routing** — each page is `React.lazy()` — initial JS bundle: shell + router only
- **Code splitting** — Vite automatically splits `vendor`, `framer-motion`, `gsap`, `@tanstack/react-query` into separate chunks
- **Static data** — `PIPELINE_STAGES` and `ENGINE_CAPABILITIES` constants are imported at build time, never fetched
- **SVG charts** — inline, no canvas, no WebGL — renders instantly with zero external dependency
- **Font loading** — `display=swap` on Google Fonts ensures text renders before fonts load
- **TanStack Query** — `staleTime: 60_000` on capabilities endpoint (data doesn't change during a session)

---

## Accessibility

- `aria-current="page"` on the active `<SidebarNavItem>`
- `role="status"` + `aria-live="polite"` on the UTC clock span
- All `<button>` elements have `type="button"` to prevent form reloads
- Focus-visible rings inherit the design system: `focus-visible:ring-1 focus-visible:ring-primary`
- Keyboard navigation: tab order follows DOM order; sidebar nav is fully keyboard-accessible
- Framer Motion `motion` components preserve `aria-*` attributes — no a11y regression

---

## Environment & Scripts

```bash
# Dev server (port 3000)
npm run dev

# Production build
npm run build

# Preview built output
npm run preview

# Lint
npm run lint

# Type-check (if TypeScript is added later)
npm run typecheck
```

`.env.development`:
```
VITE_API_BASE_URL=http://localhost:8000
```

`.env.production`:
```
VITE_API_BASE_URL=http://10.0.2.2:8000
```

---

## Implementation Order

When building, follow this sequence so each layer is complete before the next depends on it:

1. **Scaffold** — Vite project, Tailwind config with all tokens, `index.html` with fonts
2. **Shell** — `AppShell`, `Sidebar`, `TopHeader`, `useUtcClock`, `useApiStatus`
3. **Router** — 5 lazy routes wired to placeholder page components
4. **Primitives** — all `src/components/ui/` and `src/components/charts/` components
5. **Static data** — `navItems.js`, `pipelineStages.js`, `engineCapabilities.js`
6. **Services** — `api.js`, all `*Api.js` modules, TanStack Query hooks
7. **Pages** — Dashboard → Registration → RobustnessLab → Capabilities → MissionInfo
8. **Animations** — add Framer Motion and GSAP after each page renders correctly at rest
9. **Error boundaries** — wrap each lazy route
10. **Polish** — a11y audit, bundle analysis, `.env` files

---

*Generated: 2026-09-29 | Design system: Orbital Aerospace Monochrome | Target: ISRO SIH 2026*
