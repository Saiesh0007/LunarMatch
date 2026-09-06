# LunarMatch — 6 Member Documentation Pack

This package contains six role-specific documentation sets for the SIH 2026 PS 26166 prototype.

## Members

1. `Member_1_TechLead_Integration`
2. `Member_2_Data_Preprocessing`
3. `Member_3_Feature_Engineer`
4. `Member_4_Matching_Geometry`
5. `Member_5_Spatial_Metrics`
6. `Member_6_UI_Demo`

Each folder contains:

- `Architecture.md`
- `Design.md`
- `Memory.md`
- `Phases.md`
- `Project.md`
- `Rules.md`

The documents share the same project source of truth but are customized to each member's responsibilities.

## Recommended Workflow

1. Member 1 publishes the interface contract.
2. Members 2–6 work in their assigned branches.
3. Each member tests independently.
4. Member 1 integrates into `develop`.
5. UI connects only to the integrated pipeline.
6. The team freezes a known-good demo before adding optional research components.

## Git Branches

```text
main
develop
feature/preprocessing
feature/features
feature/matching
feature/spatial-metrics
feature/ui
```

## Core MVP

```text
Input
→ preprocessing
→ SIFT
→ matching
→ ratio filtering
→ RANSAC
→ registration
→ spatial balancing
→ metrics
→ visualization
```

Advanced components such as RIFT, SuperPoint, LightGlue/SuperGlue and validated sub-pixel refinement are added only after the baseline is stable.
