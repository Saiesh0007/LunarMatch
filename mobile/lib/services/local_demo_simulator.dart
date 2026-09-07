import 'dart:async';
import '../models/pipeline_model.dart';
import '../models/metrics_model.dart';

class LocalDemoSimulator {
  /// Deterministic client-side demo simulator for zero-network environments.
  /// Serves bundled demo results without duplicating computer vision algorithms in Dart.
  static Future<PipelineRunResponseModel> simulateDemoRun({
    required String pairId,
    required PipelineConfigModel config,
    required Function(PipelineStageModel stage) onStageUpdate,
  }) async {
    final stages = [
      PipelineStageModel(stageNumber: 1, name: "INPUT VALIDATION", status: "PENDING"),
      PipelineStageModel(stageNumber: 2, name: "PREPROCESSING", status: "PENDING"),
      PipelineStageModel(stageNumber: 3, name: "FEATURE EXTRACTION", status: "PENDING"),
      PipelineStageModel(stageNumber: 4, name: "FEATURE MATCHING", status: "PENDING"),
      PipelineStageModel(stageNumber: 5, name: "RATIO FILTERING", status: "PENDING"),
      PipelineStageModel(stageNumber: 6, name: "GEOMETRIC VERIFICATION", status: "PENDING"),
      PipelineStageModel(stageNumber: 7, name: "SPATIAL BALANCING", status: "PENDING"),
      PipelineStageModel(stageNumber: 8, name: "TRANSFORMATION", status: "PENDING"),
      PipelineStageModel(stageNumber: 9, name: "REGISTRATION", status: "PENDING"),
      PipelineStageModel(stageNumber: 10, name: "METRICS", status: "PENDING"),
    ];

    final stageDetails = [
      "Verified bundled lunar asset dimensions (640x640 px)",
      "Applied local CLAHE and shadow normalization",
      "Extracted 1420 keypoints (SIFT Baseline)",
      "Found 312 candidate correspondences via 2-NN search",
      "Lowe's ratio test (0.75): 118 filtered matches retained",
      "RANSAC geometric verification: 84 verified inliers",
      "Spatial grid (6x6): 28/36 occupied cells (77.8% coverage)",
      "Computed 8-DOF planar homography transformation matrix",
      "Generated registered warp and difference visualization",
      "Computed measured RMSE: 1.48 px | Confidence: HIGH",
    ];

    // Animate stages step-by-step
    for (int i = 0; i < stages.length; i++) {
      stages[i].status = "PROCESSING";
      onStageUpdate(stages[i]);
      await Future.delayed(const Duration(milliseconds: 140));

      stages[i].status = "COMPLETED";
      stages[i] = PipelineStageModel(
        stageNumber: stages[i].stageNumber,
        name: stages[i].name,
        status: "COMPLETED",
        durationMs: 12.0 + (i * 3.5),
        details: stageDetails[i],
      );
      onStageUpdate(stages[i]);
    }

    final isRejected = config.failSafeOverride;

    final metrics = isRejected
        ? RegistrationMetricsModel(
            metricMode: "SIMULATED",
            simulationSeed: 26166,
            keypointsReference: 1420,
            keypointsMoving: 1385,
            candidateMatches: 312,
            filteredMatches: 118,
            ransacInliers: 4, // Below 8 threshold
            inlierRatio: 3.4,
            spatialCoverage: 11.1,
            spatialCoverageBefore: 11.1,
            rmsePx: null, // N/A on reject
            runtimeMs: 165.0,
            confidenceLevel: "REJECTED",
            confidenceScore: 0.0,
            confidenceExplanation: "REGISTRATION NOT RELIABLE: Insufficient inliers (4 < 8 minimum threshold); Inlier ratio below 10%",
          )
        : RegistrationMetricsModel(
            metricMode: "SIMULATED",
            simulationSeed: 26166,
            keypointsReference: 1420,
            keypointsMoving: 1385,
            candidateMatches: 312,
            filteredMatches: 118,
            ransacInliers: 84,
            inlierRatio: 71.2,
            spatialCoverage: 77.8,
            spatialCoverageBefore: 38.9,
            rmsePx: 1.48,
            runtimeMs: 165.0,
            confidenceLevel: "HIGH",
            confidenceScore: 0.88,
            confidenceExplanation: "High-confidence registration with strong spatial distribution and tight reprojection error.",
          );

    final spatialStats = SpatialStatsModel(
      gridSize: config.gridSize,
      totalCells: config.gridSize * config.gridSize,
      occupiedBefore: 14,
      occupiedAfter: 28,
      coveragePercentageBefore: 38.9,
      coveragePercentageAfter: 77.8,
      coverageGainPercentage: 38.9,
    );

    return PipelineRunResponseModel(
      runId: "local_demo_seed26166",
      status: isRejected ? "NOT_RELIABLE" : "SUCCESSFUL",
      executionMode: "LOCAL FALLBACK",
      stages: stages,
      metrics: metrics,
      spatialStats: spatialStats,
      // For local demo, point directly to bundled asset images
      registeredImageUrl: 'assets/demo/pair_${pairId == 'pair_b' ? 'b' : 'a'}_mov.png',
      overlayImageUrl: 'assets/demo/pair_${pairId == 'pair_b' ? 'b' : 'a'}_ref.png',
      differenceImageUrl: 'assets/demo/pair_${pairId == 'pair_b' ? 'b' : 'a'}_ref.png',
      correspondenceImageUrl: 'assets/demo/pair_${pairId == 'pair_b' ? 'b' : 'a'}_ref.png',
      warnings: [
        "LOCAL DEMO: Running deterministic demo-result simulator using bundled assets. Backend disconnected."
      ],
      failureReason: isRejected ? "Forced fail-safe rejection in demonstration mode" : null,
      transformationMatrix: [
        [1.02, -0.05, 14.0],
        [0.05, 1.02, -10.0],
        [0.0, 0.0, 1.0]
      ],
    );
  }
}
