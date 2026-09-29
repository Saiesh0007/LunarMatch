---
name: Orbital Aerospace Monochrome
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1b1b1b'
  surface-container: '#1f1f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#c4c7c8'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#8e9192'
  outline-variant: '#444748'
  surface-tint: '#c6c6c7'
  primary: '#ffffff'
  on-primary: '#2f3131'
  primary-container: '#e2e2e2'
  on-primary-container: '#636565'
  inverse-primary: '#5d5f5f'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b4b4'
  tertiary: '#ffffff'
  on-tertiary: '#2f3034'
  tertiary-container: '#e3e2e7'
  on-tertiary-container: '#636469'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2e2e2'
  primary-fixed-dim: '#c6c6c7'
  on-primary-fixed: '#1a1c1c'
  on-primary-fixed-variant: '#454747'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e3e2e7'
  tertiary-fixed-dim: '#c6c6cb'
  on-tertiary-fixed: '#1a1b1f'
  on-tertiary-fixed-variant: '#46464b'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 24px
    letterSpacing: 0.08em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '700'
    lineHeight: 20px
    letterSpacing: 0.06em
  headline-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 17px
  label-lg:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.08em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 12px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 0.75rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.25rem
---

## Brand & Style

This design system is engineered around aerospace instrumentation, deep space mission telemetry, and mission-critical scientific rigor. It embodies extreme technical precision, high-contrast monochrome legibility, and an austere, functional aesthetic reminiscent of lunar orbiter consoles and laboratory control terminals.

Targeted at avionics engineers, computer vision researchers, and planetary scientists, the interface eliminates all decorative noise. Visual hierarchy is established strictly through stark contrast, precise micro-borders, and strict typographic scale.

Key aesthetic principles:
- **Zero Decorative Color:** Pure functional grayscale; no chromatic distractions or playful accents.
- **Instrument Surface:** Pitch-black deep space canvas paired with matte charcoal operational tiers.
- **Low-Contrast Structure:** Deliberate 1px boundary lines creating sharp visual separation without ambient blur.
- **No Glassmorphism or Skeuomorphism:** Flat, matte, deterministic surfaces optimized for immediate visual parsing and high reliability.

## Colors

The palette is strictly calibrated for dark-mode environments and mission-critical clarity:

- **Canvas Background:** `#000000` (Pitch Black) defines the deepest level, eliminating light bleed on OLED screens.
- **Surface Elevation (Cards & Panels):** `#121212` to `#161616` (Deep Charcoal) provides subtle separation from the pure black base.
- **Borders & Dividers:** `#222222` to `#262626` (Muted Iron) delivers precise 1px stroke boundaries.
- **Primary Content & Key Accents:** `#FFFFFF` (Stark White) is reserved for top-level headers, primary solid buttons, and active indicators.
- **Secondary & Auxiliary Text:** `#8E8E93` and `#A1A1AA` provide clear contrast for technical descriptions, sublabels, and inactive metadata.
- **Input & Display Wells:** `#0A0A0A` to `#0D0D0D` (Obsidian Recesses) for image viewports and monospace text fields.

## Typography

The typographical hierarchy is engineered for high legibility under dense telemetry conditions. 

- **Primary Navigation & Headers:** Set in uppercase `Space Grotesk` with prominent tracking (`0.06em` to `0.08em`) to mimic aerospace telemetry readouts.
- **Descriptive & Body Content:** Set in `Inter` with neutral kerning, balanced line heights, and medium gray tints for effortless reading without eye fatigue.
- **Technical Readouts, Badges, & Steppers:** Set in `JetBrains Mono` for rigid vertical alignment of values, API URLs, step indices, and model identifiers.

## Layout & Spacing

The layout is built for compact mobile instrumentation and high data density:

- **Grid & Alignments:** Strict vertical flow on mobile screens, utilizing a 16px (`1rem`) outer margin from the device boundaries.
- **Card Padding:** Standardized 12px to 16px internal padding for cards and technical modules.
- **Component Stacking:** Consistent 10px to 12px gaps between sequential cards, maintaining modular grouping without wasting vertical space.
- **Responsive Adaptations:**
  - *Mobile (< 640px):* Single-column card stacking, full-width actions, fixed bottom navigation bar (64px height).
  - *Tablet & Desktop (≥ 640px):* 2 to 3 column modular grids with 16px gutters, retaining pitch black outer margins and max content bounds (840px for single-path workflows).

## Elevation & Depth

This design system rejects ambient drop shadows, colored halos, and blurred glassmorphism. Depth is achieved purely through **tonal stacking** and **crisp 1px boundary strokes**:

- **Ground Level (Elevation 0):** `#000000` base canvas.
- **Container Level (Elevation 1):** `#121212` or `#161616` background with a continuous `1px solid #222222` or `#262626` outline.
- **Inner Well / Display Target (Elevation -1):** `#080808` inset surfaces with a `1px solid #1C1C1C` border (used for camera viewports, code entry boxes, and file drop zones).
- **Active Floating Elements:** Bottom action bars and fixed headers sit on `#000000` or `#0E0E0E` with a single top/bottom divider border of `#222222`.

## Shapes

The geometric structure balances precision engineering with modern ergonomic handheld feel:

- **Structural Cards & Containers:** Radii strictly set to `14px` - `16px` (`rounded-lg`), producing smooth enclosures that stand out against the `#000000` background.
- **Primary Buttons & Floating Triggers:** Fully rounded pill shapes (`rounded-full` or 9999px) for single-action emphasis, or structured 10px–12px radius for full-width instrument controls.
- **Filter Chips & Segmented Toggles:** Compact 8px to 10px rounded rectangles.
- **Step Counters & Badges:** Squircle / 8px rounded boxes creating miniature technical tags.

## Components

### Buttons
- **Primary Action:** Solid `#FFFFFF` fill with `#000000` bold typography (`Space Grotesk` or `Inter`, uppercase), 12px vertical padding, pill or 12px border radius. No border, zero shadow.
- **Secondary / Ghost Outlined:** Background transparent or `#161616`, `1px solid #333333` border, text `#FFFFFF` or `#8E8E93`.
- **Icon Buttons:** Pitch black or `#161616` background, square/circular 40px bounding box, muted white stroke icons.

### Cards & Telemetry Containers
- Container fill: `#121212` to `#161616`.
- Border: `1px solid #242424`.
- Padding: 16px.
- Corner Radius: 14px–16px.
- Internal Typography: White uppercase header, followed by muted `#8E8E93` parameter descriptions.

### Chips & Segmented Controls
- **Segmented Control Bar:** Enclosed inside a `#0D0D0D` container with a `1px solid #222222` perimeter border.
- **Selected Segment:** Pure `#FFFFFF` background with pitch black `#000000` text, bold weight.
- **Unselected Segment:** Background transparent, text `#8E8E93`, hover/touch tint `#1A1A1A`.

### Status Badges & Step Indices
- Monochrome step indicators: `#1A1A1A` background, `1px solid #2B2B2B` border, monospaced text in stark white.
- Status Chips: Dark gray outline with accompanying status dot (solid white for online/verified, hollow or muted gray for offline).

### Input Fields & Monospace Editors
- Input surface: `#0A0A0A` inset.
- Border: `1px solid #262626`, focusing to `1px solid #FFFFFF`.
- Typography: `JetBrains Mono` for URL and technical parameter inputs, colored `#FFFFFF`.
- Labeling: Floating or top-aligned uppercase label in `#8E8E93` at 11px.

### Navigation Bars
- **Header:** Sticky pitch black (`#000000`), centered or left-aligned uppercase bold headline with back caret icon (20px).
- **Bottom Navigation Dock:** Deep black background, `1px solid #1E1E1E` top edge, active icon housed in an elongated capsule highlight (`#1E1E1E` or solid white pill icon), accompanied by crisp labels.