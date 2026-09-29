# Component Catalog

This document explains the reusable React components found in `src/components/ui`.

## 1. `Button` (`Button.jsx`)
Framer-motion powered button supporting multiple visual variants and a built-in loading spinner.
```jsx
<Button variant="primary" icon="upload" loading={false}>
  Upload File
</Button>
```
**Variants:** `primary`, `ghost`, `icon`

## 2. `Chip` (`Chip.jsx`)
Stateful toggle item providing fluid highlight animations across a group (via Framer Motion `layoutId`). 
```jsx
<Chip 
  layoutId="unique-group-id" 
  label="Homography" 
  active={true} 
  onClick={() => {}} 
/>
```

## 3. `TelemetryRow` (`TelemetryRow.jsx`)
Uniform row component handling tabular formatting and standard badge outputs for API status responses.
```jsx
<TelemetryRow 
  id="JOB-489" 
  inliers={842} 
  rmse={1.04} 
  status="warning" 
/>
```

## 4. `ImageViewport` (`ImageViewport.jsx`)
Isolated smart component for uploading local file datasets using standard `input type="file"`, automatically generating blob-based preview arrays while preserving UI aesthetics.

## 5. `MetricCard` (`MetricCard.jsx`)
Displays numeric value counters escalating smoothly using a Framer Motion `useSpring` and `useTransform` effect to count up to the KPI threshold dynamically.
