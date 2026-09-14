class RegistrationMetricsModel {
  final String metricMode; // "MEASURED" or "DEMO"
  final int? simulationSeed;
  final int keypointsReference;
  final int keypointsMoving;
  final int candidateMatches;
  final int filteredMatches;
  final int ransacInliers;
  final double inlierRatio;
  final double spatialCoverage;
  final double spatialCoverageBefore;
  final double? rmsePx;
  final double runtimeMs;
  final String confidenceLevel; // "HIGH", "MEDIUM", "LOW", "REJECTED"
  final double confidenceScore; // 0.0 - 1.0
  final String confidenceExplanation;

  const RegistrationMetricsModel({
    required this.metricMode,
    this.simulationSeed,
    required this.keypointsReference,
    required this.keypointsMoving,
    required this.candidateMatches,
    required this.filteredMatches,
    required this.ransacInliers,
    required this.inlierRatio,
    required this.spatialCoverage,
    required this.spatialCoverageBefore,
    this.rmsePx,
    required this.runtimeMs,
    required this.confidenceLevel,
    required this.confidenceScore,
    required this.confidenceExplanation,
  });

  factory RegistrationMetricsModel.fromJson(Map<String, dynamic> json) {
    return RegistrationMetricsModel(
      metricMode: json['metric_mode'] ?? 'MEASURED',
      simulationSeed: json['simulation_seed'],
      keypointsReference: json['keypoints_reference'] ?? 0,
      keypointsMoving: json['keypoints_moving'] ?? 0,
      candidateMatches: json['candidate_matches'] ?? 0,
      filteredMatches: json['filtered_matches'] ?? 0,
      ransacInliers: json['ransac_inliers'] ?? 0,
      inlierRatio: (json['inlier_ratio'] as num?)?.toDouble() ?? 0.0,
      spatialCoverage: (json['spatial_coverage'] as num?)?.toDouble() ?? 0.0,
      spatialCoverageBefore: (json['spatial_coverage_before'] as num?)?.toDouble() ?? 0.0,
      rmsePx: (json['rmse_px'] as num?)?.toDouble(),
      runtimeMs: (json['runtime_ms'] as num?)?.toDouble() ?? 0.0,
      confidenceLevel: json['confidence_level'] ?? 'LOW',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.0,
      confidenceExplanation: json['confidence_explanation'] ?? '',
    );
  }
}

class SpatialStatsModel {
  final int gridSize;
  final int totalCells;
  final int occupiedBefore;
  final int occupiedAfter;
  final double coveragePercentageBefore;
  final double coveragePercentageAfter;
  final double coverageGainPercentage;

  const SpatialStatsModel({
    required this.gridSize,
    required this.totalCells,
    required this.occupiedBefore,
    required this.occupiedAfter,
    required this.coveragePercentageBefore,
    required this.coveragePercentageAfter,
    required this.coverageGainPercentage,
  });

  factory SpatialStatsModel.fromJson(Map<String, dynamic> json) {
    return SpatialStatsModel(
      gridSize: json['grid_size'] ?? 6,
      totalCells: json['total_cells'] ?? 36,
      occupiedBefore: json['occupied_cells_before'] ?? 0,
      occupiedAfter: json['occupied_cells_after'] ?? 0,
      coveragePercentageBefore: (json['coverage_percentage_before'] as num?)?.toDouble() ?? 0.0,
      coveragePercentageAfter: (json['coverage_percentage_after'] as num?)?.toDouble() ?? 0.0,
      coverageGainPercentage: (json['coverage_gain_percentage'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
