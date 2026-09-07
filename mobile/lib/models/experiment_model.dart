class RobustnessPointModel {
  final double variationValue;
  final String variationLabel;
  final int inliers;
  final double inlierRatio;
  final double spatialCoverage;
  final double? rmsePx;
  final double runtimeMs;
  final String status;

  const RobustnessPointModel({
    required this.variationValue,
    required this.variationLabel,
    required this.inliers,
    required this.inlierRatio,
    required this.spatialCoverage,
    this.rmsePx,
    required this.runtimeMs,
    required this.status,
  });

  factory RobustnessPointModel.fromJson(Map<String, dynamic> json) {
    return RobustnessPointModel(
      variationValue: (json['variation_value'] as num?)?.toDouble() ?? 0.0,
      variationLabel: json['variation_label'] ?? '',
      inliers: json['inliers'] ?? 0,
      inlierRatio: (json['inlier_ratio'] as num?)?.toDouble() ?? 0.0,
      spatialCoverage: (json['spatial_coverage'] as num?)?.toDouble() ?? 0.0,
      rmsePx: (json['rmse_px'] as num?)?.toDouble(),
      runtimeMs: (json['runtime_ms'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] ?? 'FAILED',
    );
  }
}

class RobustnessExperimentModel {
  final String experimentId;
  final String experimentType;
  final String baseImageId;
  final String disclaimer;
  final List<RobustnessPointModel> points;
  final Map<String, dynamic> summary;

  const RobustnessExperimentModel({
    required this.experimentId,
    required this.experimentType,
    required this.baseImageId,
    required this.disclaimer,
    required this.points,
    required this.summary,
  });

  factory RobustnessExperimentModel.fromJson(Map<String, dynamic> json) {
    return RobustnessExperimentModel(
      experimentId: json['experiment_id'] ?? '',
      experimentType: json['experiment_type'] ?? '',
      baseImageId: json['base_image_id'] ?? '',
      disclaimer: json['disclaimer'] ?? 'CONTROLLED SYNTHETIC EXPERIMENT',
      points: (json['points'] as List<dynamic>?)
              ?.map((e) => RobustnessPointModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      summary: json['summary'] ?? {},
    );
  }
}
