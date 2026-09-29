# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Frontend Is

This is a modern React SPA using Vite, Tailwind CSS 4, React Router, Zustand, and Framer Motion.
It serves as the Web Workstation for LunarMatch's mission-control dashboard.

## Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

## Architecture & Tech Stack

- **React 19**
- **Vite 6**
- **Tailwind CSS 4**
- **Zustand** - For global app state management
- **React Router** - For component-based routing
- **Framer Motion 12** - For fluid route transitions and layout animations
- **Lucide React** & **Material Symbols Outlined** - For iconography

## Structure

```
frontend/
  src/
    components/
      layout/     # AppShell, Header, Sidebar
      ui/         # Resuable core components (Button, Chip, SectionHeader, etc)
    data/         # Static data / mocks
    pages/        # Route pages (Dashboard, Registration/Pipeline, RobustnessLab, Capabilities)
    store/        # Zustand state
    utils/        # Helpers
  docs/           # Documentation (ARCHITECTURE.md, SETUP.md, DESIGN.md, COMPONENTS.md)
  public/         # Static assets
```

## Design System: Orbital Aerospace Monochrome

The **Orbital Aerospace Monochrome** design system governs all visual decisions. Key rules (full spec in `docs/DESIGN.md`):

- **Background hierarchy (darkest → lightest):**
  - base: `#000000`
  - `surface-container-lowest`: `#0e0e0e`
  - `surface-container-low`: `#1b1b1b`
  - `surface-container`: `#1f1f1f`
  - `surface-container-high`: `#2a2a2a`
  - `surface-container-highest`: `#353535`
- **Primary accent:** `#ffffff` only — used for active elements, top-level headings, and primary buttons (solid white fill, black text).
- **Muted text:** `outline` (`#8e9192`) / `on-surface-variant` (`#c4c7c8`).
- **Borders:** `1px solid` in the `#222–#333` range; no drop shadows or glassmorphism.
- **Fonts by role:**
  - Headers / nav labels → `Space Grotesk`, uppercase, tracked (`0.06–0.08em`): use `font-headline-lg/md`, `font-label-lg`.
  - Body / descriptions → `Inter`: use `font-body-lg/md`, `font-headline-sm`.
  - Numeric readouts, badges, API URLs → `JetBrains Mono`: use `font-label-md/sm` or `font-mono`.
- **Card shape:** `rounded-xl` (14–16px) for primary containers; `rounded-lg` for inner modules.
- **Hover/Active logic**: Rely on standard token modifiers and specific class lists. The theme focuses on stark monochrome contrast without extraneous effects.

All actual tokens are pre-defined in Tailwind's CSS variable setup (see `src/index.css`) — use standard utility classes (`bg-surface-container`, `text-outline`, etc.) and do not use raw hex values in markup.