# LunarMatch — Simulation and Offline Modes

**Fixed seed:** `26166` (the SIH 2026 problem-statement number).

LunarMatch normally runs the live pipeline. Three other modes exist so a
demonstration never depends on a network or on heavy computation. Each one is
labelled where it runs.

| Mode | Where | Trigger | Label |
| :--- | :--- | :--- | :--- |
| Backend simulation | backend | `simulation_mode: true` (or `is_demo_mode`) in the run request | `execution_mode: demo`, `metric_mode: demo`, `simulation_seed: 26166` |
| Web offline simulation | web Studio | backend unreachable | header shows `FLIGHT SIMULATION`; button reads *EXECUTE REGISTRATION ENGINE (SIMULATED)* |
| Mobile local demo | mobile app | backend unreachable, or offline forced on the About screen | offline status on About; demo results replayed |

---

## 1. Backend simulation (`app/simulation/simulator.py`)

`DeterministicSimulator` replaces feature matching with a deterministic model:

- the sensor pair sets a domain-gap penalty (e.g. optical vs infrared),
- the radiometric difference between the two images reduces the correspondence count,
- synthesized correspondences are spread over the grid and coverage is computed
  with the same `SpatialBalancing` code as live runs,
- the same metric rules decide status and confidence, so a simulated run can
  still be `NOT_RELIABLE`.

Every simulated run writes the same artifact set as a live run to
`backend/outputs/run_<id>/`. Identical inputs give identical outputs.

## 2. Web offline simulation

With the backend offline, the Studio animates its five stages and shows the
selected preset pair's sample values from `web/app/data/lunarData.ts`. No image
processing happens in the browser. Metric cards appear after the simulated run,
like after a live run.

## 3. Mobile local demo (`mobile/lib/services/local_demo_simulator.dart`)

Replays bundled results for the demo pairs, stage by stage, without duplicating
any computer-vision code in Dart. The robustness screen generates an offline
sweep result in the same situation.

---

## What is not simulated

In live mode every algorithm runs for real, including the learned models:
SuperPoint, SuperGlue and LightGlue run as PyTorch CPU inference with pretrained
weights, and fall back to RIFT2 when the weights are missing.

`app/vision/superglue_matcher.py` also contains a pure-NumPy Sinkhorn
optimal-transport matcher (sinusoidal position encoding, dustbin augmentation,
log-domain Sinkhorn, mutual-nearest-neighbour assignment). It is exercised by the
unit tests; the pipeline's `matcher: superglue` uses the neural SuperGlue model.
