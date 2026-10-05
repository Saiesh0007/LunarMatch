# LunarMatch — Design System

Both apps share one monochrome "mission control" look: black backgrounds, grey
surfaces, white text and accents, monospaced telemetry. Status is conveyed by
labels and badges (e.g. `OPTIMAL (PASS)` / `FAIL-SAFE`, `REGISTRATION SUCCESSFUL`
/ `REGISTRATION NOT RELIABLE`) rather than by colour. The only hues are the
correspondence colours in the web app.

Sources: `web/app/globals.css` (CSS variables) and `mobile/lib/app/theme.dart`
(`LunarTheme`).

## 1. Colour palette

| Role | Value | Web variable | Mobile constant |
| :--- | :--- | :--- | :--- |
| Background | `#000000` | `--bg-primary` | `background` |
| Background, subtle | `#050505` | `--bg-subtle` | `backgroundSubtle` |
| Surface | `#101010` | `--surface` | `surface` |
| Card | `#141414` | `--surface-card` | `surfaceCard` |
| Elevated surface | `#1C1C1C` | `--surface-elevated` | `surfaceElevated` |
| Highlight | `#242424` | `--surface-highlight` | `surfaceHighlight` |
| Border | `#2E2E2E` | `--border` | `border` |
| Border, light | `#3A3A3A` | `--border-light` | `borderLight` |
| Border, focus | `#666666` | `--border-focus` | `borderFocus` |
| Text, primary | `#FFFFFF` | `--text-primary` | `textPrimary` |
| Text, secondary | `#B0B0B0` | `--text-secondary` | `textSecondary` |
| Text, tertiary | `#777777` | `--text-tertiary` | `textTertiary` |
| Disabled | `#555555` | `--text-disabled` | `disabled` |
| Accent | `#FFFFFF` | `--accent` | `accent` |

Mobile status constants are greys too: success `#FFFFFF`, warning `#B8B8B8`,
error `#E2E2E2`, neutral `#888888`.

**Correspondence colours (web):** inliers light green `#86EFAC` (solid lines),
outliers light red `#FCA5A5` (dashed lines). Line style also distinguishes them
without colour.

## 2. Typography

- **Web:** Geist for text, Geist Mono for telemetry, coordinates, badges and the
  log (`next/font/google`).
- **Mobile:** system sans-serif for text; Courier / monospace for telemetry.
- Headings and badges: bold uppercase with wide letter spacing.

## 3. Information hierarchy

1. Decision — success / not-reliable badge or banner.
2. Visual comparison — split slider, overlay / blink, checkerboard, difference map.
3. Metric cards — keypoints, candidates, inliers, inlier ratio, RMSE, coverage,
   latency, decision.
4. Detail — correspondences, spatial grid, stage log, robustness sweeps.

## 4. Layout

- **Web:** two-column Studio (configuration | viewer and results) that stacks to
  one column on phones; tabs are reachable by URL hash. See
  [WebApp.md](WebApp.md).
- **Mobile:** scrollable screens (`SingleChildScrollView`) with adaptive grids
  (`LayoutBuilder`, `Wrap`) from phones to Windows desktop windows.
