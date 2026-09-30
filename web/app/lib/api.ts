/**
 * LUNARMATCH FastAPI client.
 * Base URL is configurable via NEXT_PUBLIC_API_URL (defaults to the local backend).
 */

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export type RegistrationStatus = "SUCCESSFUL" | "LOW_CONFIDENCE" | "NOT_RELIABLE" | "FAILED";

export interface PipelineStage {
  stage_number: number;
  name: string;
  status: string;
  duration_ms: number;
  details?: string | null;
}

export interface PipelineMetrics {
  keypoints_reference: number;
  keypoints_moving: number;
  candidate_matches: number;
  filtered_matches: number;
  ransac_inliers: number;
  inlier_ratio: number; // percentage 0-100
  spatial_coverage: number; // percentage 0-100
  spatial_coverage_before: number;
  rmse_px: number | null;
  runtime_ms: number;
  confidence_level: string;
  confidence_score: number;
  confidence_explanation: string;
}

export interface PipelineRunResponse {
  run_id: string;
  status: RegistrationStatus;
  execution_mode: string;
  stages: PipelineStage[];
  metrics: PipelineMetrics;
  outputs: {
    registered_image_url?: string | null;
    overlay_image_url?: string | null;
    difference_image_url?: string | null;
    correspondence_image_url?: string | null;
    artifacts_dir: string;
  };
  warnings: string[];
  failure_reason?: string | null;
}

export interface PipelineRunRequest {
  reference_image_id: string;
  moving_image_id: string;
  feature_method?: string;
  ransac_threshold?: number;
  subpixel_refinement?: boolean;
  spatial_balancing?: boolean;
}

export interface ImageUploadResponse {
  image_id: string;
  filename: string;
  width: number;
  height: number;
  preview_url: string;
}

async function request<T>(path: string, init?: RequestInit, timeoutMs = 120000): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, { ...init, signal: controller.signal });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      } catch {
        // Non-JSON error body
      }
      throw new Error(`${res.status} ${detail}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

/** Resolve a backend-relative URL (e.g. artifact paths) to an absolute one. */
export const apiUrl = (path: string) => `${API_BASE_URL}${path}`;

export async function checkHealth(): Promise<boolean> {
  try {
    await request<{ status: string }>("/health", undefined, 2000);
    return true;
  } catch {
    return false;
  }
}

export function runPipeline(body: PipelineRunRequest): Promise<PipelineRunResponse> {
  return request<PipelineRunResponse>("/api/v1/pipeline/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function uploadImage(file: Blob, filename: string): Promise<ImageUploadResponse> {
  const form = new FormData();
  form.append("file", file, filename);
  return request<ImageUploadResponse>("/api/v1/images/upload", { method: "POST", body: form });
}

/** The most recent Studio run, shared with the Correspondence and Robustness tabs. */
export interface StudioSession {
  run: PipelineRunResponse;
  refSrc: string;
  movSrc: string; // un-registered moving image (tie-point coordinates are in this frame)
  refImageId: string;
  movImageId: string;
  featureMethod: string;
  isCustom: boolean;
}

export interface MatchRecord {
  ref_pt: [number, number];
  mov_pt: [number, number];
  distance: number;
  is_inlier: boolean;
  is_spatially_selected?: boolean;
}

/** Filtered matches (with MAGSAC inlier flags) persisted for a run. */
export function getRunMatches(runId: string): Promise<MatchRecord[]> {
  return request<MatchRecord[]>(`/api/v1/results/${runId}/artifact/matches_filtered.json`);
}

export interface RobustnessPoint {
  variation_value: number;
  variation_label: string;
  inliers: number;
  inlier_ratio: number; // percentage 0-100
  spatial_coverage: number; // percentage 0-100
  rmse_px: number | null;
  runtime_ms: number;
  status: RegistrationStatus;
}

export interface RobustnessExperimentResponse {
  experiment_id: string;
  experiment_type: string;
  base_image_id: string;
  disclaimer: string;
  points: RobustnessPoint[];
  summary: Record<string, unknown>;
}

export function runRobustnessExperiment(body: {
  base_image_id: string;
  experiment_type: string;
  feature_method?: string;
  variation_steps?: number;
  min_val?: number;
  max_val?: number;
}): Promise<RobustnessExperimentResponse> {
  return request<RobustnessExperimentResponse>(
    "/api/v1/experiments/robustness",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
    600000
  );
}
