# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Frontend Is

This is **not** a Node.js/npm project. There is no build step, no package manager, and no framework. The frontend consists of four standalone HTML files — each a self-contained screen that runs directly in a browser with no compilation required.

**To open a screen:** Just open `code.html` in a browser (or serve with any static file server):
```bash
# Quick local preview — pick any screen
python3 -m http.server 8080 --directory stitch_lunarmatch_frontend_application/lunarmatch_workstation_dashboard/
# Then open http://localhost:8080/code.html
```

There is no lint command, no test runner, and no build command. Edits to `code.html` take effect on the next browser refresh.

## Screens & Structure

All screens live under `stitch_lunarmatch_frontend_application/`, one folder per screen:

| Folder | Screen | Nav path |
|---|---|---|
| `lunarmatch_workstation_dashboard/` | Main mission-control dashboard with telemetry KPIs | `01 // CORE` |
| `lunar_registration_studio/` | Image upload + pipeline configuration wizard | `02 // PIPELINE` |
| `robustness_laboratory_workstation/` | Stress-test runner with step-by-step pipeline inspector | `03 // STRESS-TEST` |
| `capabilities_architecture/` | Engine spec & 9-stage pipeline documentation | `04 // ENGINE SPEC` |

Each folder also has a `screen.png` reference screenshot. The `orbital_aerospace_monochrome/DESIGN.md` file is the design-system specification (not a screen).

## Tech Stack

- **Tailwind CSS** — loaded from CDN (`https://cdn.tailwindcss.com`). The Tailwind config is inlined in a `<script id="tailwind-config">` block at the top of every HTML file.
- **Google Fonts** — Inter (body), Space Grotesk (headlines), JetBrains Mono (technical readouts), Material Symbols Outlined (icons).
- **Vanilla JS** — minimal, written as an IIFE at the bottom of each file. No framework, no modules.
- **No backend calls** — the current HTML files are UI prototypes. The backend (`FastAPI` at `10.0.2.2:8000`) is referenced in the UI copy but no actual `fetch()` calls exist yet.

## Design System

The **Orbital Aerospace Monochrome** design system governs all visual decisions. Key rules (full spec in `orbital_aerospace_monochrome/DESIGN.md`):

- **Background hierarchy (darkest → lightest):** `#000000` → `#0e0e0e` (`surface-container-lowest`) → `#1b1b1b` (`surface-container-low`) → `#1f1f1f` (`surface-container`) → `#2a2a2a` (`surface-container-high`) → `#353535` (`surface-container-highest`).
- **Primary accent:** `#ffffff` only — used for active elements, top-level headings, and primary buttons (solid white fill, black text).
- **Muted text:** `#8e9192` (`outline`) / `#c4c7c8` (`on-surface-variant`).
- **Borders:** `1px solid` in the `#222–#333` range; no drop shadows or glassmorphism.
- **Fonts by role:**
  - Headers / nav labels → `Space Grotesk`, uppercase, tracked (`0.06–0.08em`): use `font-headline-lg/md`, `font-label-lg`.
  - Body / descriptions → `Inter`: use `font-body-lg/md`, `font-headline-sm`.
  - Numeric readouts, badges, API URLs → `JetBrains Mono`: use `font-label-md/sm` or `font-mono`.
- **Card shape:** `rounded-xl` (14–16px) for primary containers; `rounded-lg` for inner modules.
- **Active/selected state:** Swap background to `bg-primary` (`#ffffff`) + text `text-on-primary` (`#000000`) + `font-bold`. Inactive state uses `text-on-surface-variant` + `hover:bg-surface-container`.

All Tailwind tokens (`surface-container-low`, `outline`, `on-surface-variant`, etc.) are pre-defined in the inline `tailwind.config` block — use them, do not use raw hex values in markup.

## Shared Shell Pattern

Every screen shares the same structural shell:
1. **Left sidebar** (`<aside>`, `w-72`, fixed) — logo, nav links with `data-path` attributes, a node-status widget, and a user identity row at the bottom.
2. **Top header** (`<header>`, `h-16`, fixed, `left-72`) — breadcrumb, UTC clock, FastAPI status chip, and Raw Logs button.
3. **Main content** (`<main>`, `pt-16 pl-72`) — the unique content of each screen.

When adding a new screen, copy the sidebar + header verbatim from an existing file. Only alter `aria-current="page"` on the correct nav `<a>`.

## JavaScript Conventions

- All JS lives in a single IIFE at the bottom of the file, just before `</body>`.
- DOM queries are done inside the IIFE; no global variables.
- Interactive state (active pill selection, button feedback) is managed by toggling Tailwind class strings directly — there is no state library.
- Async feedback is simulated with `setTimeout`; real fetch integration to the backend has not been wired up yet.
