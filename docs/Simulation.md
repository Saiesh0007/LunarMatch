# LunarMatch — Deterministic Simulation Engine

**Fixed Seed:** `26166` (derived from SIH 2026 Problem Statement ID)

---

## 1. Purpose & Motivation
The demonstration MVP must provide an ultra-reliable presentation experience that does not crash or stall in zero-network environments, while strictly adhering to scientific honesty.
Rather than training a deep neural network or claiming untested sub-pixel capabilities, LunarMatch incorporates a **deterministic simulation engine**.

## 2. Core Operational Rules
1. **Never Present Simulation as Real Model Execution:**
   - Any run executed under simulation is tagged with `metric_mode: "SIMULATED"` and `simulation_seed: 26166`.
   - The UI prominently displays `SIMULATED PIPELINE` or `LOCAL DEMO`.
2. **Logically Coherent Physical Relationships:**
   - Metrics are NOT randomly generated numbers. They follow deterministic mathematical functions based on input attributes:
     - **Illumination Delta ($\Delta I$):** As radiometric difference increases, feature descriptor matchability degrades non-linearly.
     - **Multi-Modal Domain Gap:** Sensor mismatch (e.g. Optical vs Hyperspectral) applies a domain gap penalty to inlier ratios.
     - **Spatial Distribution:** Feature points are partitioned into an $N \times N$ grid; occupied cells and coverage gains are calculated explicitly.
3. **Fail-Safe Integrity:**
   - Simulation mode does NOT guarantee a successful registration.
   - If an input pair is severely degraded or the fail-safe trigger is engaged, the simulation faithfully outputs `REGISTRATION NOT RELIABLE` with precise diagnostic reasons.
4. **Complete Artifact Generation:**
   - Every simulated run writes the identical 13 artifact files to `outputs/run_<id>/` (including JSON feature sets, coordinates, warped registered image, overlay, difference map, and experiment log).
