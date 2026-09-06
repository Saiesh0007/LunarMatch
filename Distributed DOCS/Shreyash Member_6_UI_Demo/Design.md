# LunarMatch — UI + Demo Engineer Design

## Goal

Streamlit application, visualization, controls, results dashboard, demo reliability

## Files Owned

- `app.py`
- UI-specific visualization helpers

## Main UI

Provide:
- reference image upload
- moving image upload
- sensor selectors
- method selector for implemented methods
- run button
- pipeline status
- correspondence visualization
- registered overlay
- metrics

## Result Contract

Call only:

```python
result = run_lunarmatch(...)
```

The UI should not implement SIFT, RANSAC or metrics itself.

## Failure UI

Display clear reasons for failed registration rather than a misleading image.

## Demo Mode

Keep a known-good example accessible locally so the presentation can be recovered quickly if file selection or input causes problems.

## Advanced Controls

Do not show options for algorithms that are not actually implemented.

## Visual Priority

```text
Registered result
>
Correspondence visualization
>
Metrics
>
Pipeline status
>
Configuration
```

## Demo Requirement

A panel member should understand the result without reading source code.

## Failure Requirement

The system should explain when a registration is unreliable.
