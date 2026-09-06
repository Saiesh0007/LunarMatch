# LunarMatch — Matching + Geometry Engineer Development Phases

## Phase 1 — Contract

Confirm the input/output interface with Member 1.

## Phase 2 — Independent Implementation

Implement the smallest reliable version of the assigned module.

## Phase 3 — Unit Testing

Test normal input, difficult input and invalid input.

## Phase 4 — Integration

Merge into `develop` only after the module passes its tests.

## Phase 5 — Demo Hardening

Use the team's known-good lunar image pair and verify deterministic output.

## Phase 6 — Advanced Work

Only after the baseline is stable, work on advanced functionality relevant to this role.

## Emergency Rule

If an advanced component threatens the working demo, preserve the verified baseline and mark the advanced component experimental/planned.

## Phase 1

BF/FLANN matching.

## Phase 2

Ratio filtering.

## Phase 3

RANSAC geometric verification.

## Phase 4

Registration/warping.

## Phase 5

Stress-test false matches.

## Phase 6

Optional robust-estimation or learned matcher experiment.

The registration engine must remain usable without the advanced matcher.
