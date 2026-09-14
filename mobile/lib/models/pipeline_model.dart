import 'metrics_model.dart';

class PreprocessingConfigModel {
  bool normalize;
  bool clahe;
  bool denoise;
  double clipLimit;
  int tileGridSize;

  PreprocessingConfigModel({
    this.normalize = true,
    this.clahe = true,
    this.denoise = true,
    this.clipLimit = 2.0,
    this.tileGridSize = 8,
  });

  Map<String, dynamic> toJson() => {
    'normalize': normalize,
    'clahe': clahe,
    'denoise': denoise,
    'clip_limit': clipLimit,
    'tile_grid_size': tileGridSize,
  };

  factory PreprocessingConfigModel.fromJson(Map<String, dynamic> json) {
    return PreprocessingConfigModel(
      normalize: json['normalize'] ?? true,
      clahe: json['clahe'] ?? true,
      denoise: json['denoise'] ?? true,
      clipLimit: (json['clip_limit'] as num?)?.toDouble() ?? 2.0,
      tileGridSize: json['tile_grid_size'] ?? 8,
    );
  }
}

class PipelineConfigModel {
  String featureMethod; // "SIFT", "RIFT2", "SuperPoint"
  String matcher; // "BF", "FLANN"
  double ratioThreshold;
  String geometricModel; // "affine", "homography"
  bool spatialBalancing;
  int gridSize;
  int maxPerCell;
  double ransacThreshold;
  int maxFeatures;
  PreprocessingConfigModel preprocessing;
  bool simulationMode;
  bool failSafeOverride;

  PipelineConfigModel({
    this.featureMethod = "SIFT",
    this.matcher = "BF",
    this.ratioThreshold = 0.75,
    this.geometricModel = "homography",
    this.spatialBalancing = true,
    this.gridSize = 6,
    this.maxPerCell = 5,
    this.ransacThreshold = 3.0,
    this.maxFeatures = 2000,
    PreprocessingConfigModel? preprocessing,
    this.simulationMode = false,
    this.failSafeOverride = false,
  }) : preprocessing = preprocessing ?? PreprocessingConfigModel();

  Map<String, dynamic> toJson() => {
    'feature_method': featureMethod,
    'matcher': matcher,
    'ratio_threshold': ratioThreshold,
    'geometric_model': geometricModel,
    'spatial_balancing': spatialBalancing,
    'grid_size': gridSize,
    'max_features_per_cell': maxPerCell,
    'ransac_threshold': ransacThreshold,
    'max_features': maxFeatures,
    'preprocessing': preprocessing.toJson(),
    'simulation_mode': simulationMode,
    'fail_safe_override': failSafeOverride,
  };
}

class PipelineStageModel {
  final int stageNumber;
  final String name;
  String status; // "PENDING", "PROCESSING", "COMPLETED", "FAILED", "SKIPPED"
  final double durationMs;
  final String? details;

  PipelineStageModel({
    required this.stageNumber,
    required this.name,
    this.status = "PENDING",
    this.durationMs = 0.0,
    this.details,
  });

  factory PipelineStageModel.fromJson(Map<String, dynamic> json) {
    return PipelineStageModel(
      stageNumber: json['stage_number'] ?? 0,
      name: json['name'] ?? '',
      status: json['status'] ?? 'PENDING',
      durationMs: (json['duration_ms'] as num?)?.toDouble() ?? 0.0,
      details: json['details'],
    );
  }
}

class PipelineRunResponseModel {
  final String runId;
  final String status; // "SUCCESSFUL", "LOW_CONFIDENCE", "NOT_RELIABLE", "FAILED"
  final String executionMode; // "LIVE BASELINE", "DEMO SIMULATION", "LOCAL FALLBACK"
  final List<PipelineStageModel> stages;
  final RegistrationMetricsModel metrics;
  final SpatialStatsModel? spatialStats;
  final String? registeredImageUrl;
  final String? overlayImageUrl;
  final String? differenceImageUrl;
  final String? correspondenceImageUrl;
  final List<String> warnings;
  final String? failureReason;
  final List<List<double>>? transformationMatrix;
  final Map<String, dynamic>? configuration;

  PipelineRunResponseModel({
    required this.runId,
    required this.status,
    required this.executionMode,
    required this.stages,
    required this.metrics,
    this.spatialStats,
    this.registeredImageUrl,
    this.overlayImageUrl,
    this.differenceImageUrl,
    this.correspondenceImageUrl,
    this.warnings = const [],
    this.failureReason,
    this.transformationMatrix,
    this.configuration,
  });

  factory PipelineRunResponseModel.fromJson(Map<String, dynamic> json) {
    var outputs = json['outputs'] as Map<String, dynamic>?;
    var stagesList = (json['stages'] as List<dynamic>?)
            ?.map((e) => PipelineStageModel.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    List<List<double>>? matrix;
    if (json['transformation_matrix'] != null) {
      matrix = (json['transformation_matrix'] as List<dynamic>)
          .map((row) => (row as List<dynamic>).map((e) => (e as num).toDouble()).toList())
          .toList();
    }

    return PipelineRunResponseModel(
      runId: json['run_id'] ?? '',
      status: json['status'] ?? 'FAILED',
      executionMode: json['execution_mode'] ?? 'LIVE BASELINE',
      stages: stagesList,
      metrics: RegistrationMetricsModel.fromJson(json['metrics'] ?? {}),
      spatialStats: json['spatial_stats'] != null
          ? SpatialStatsModel.fromJson(json['spatial_stats'])
          : null,
      registeredImageUrl: outputs?['registered_image_url'],
      overlayImageUrl: outputs?['overlay_image_url'],
      differenceImageUrl: outputs?['difference_image_url'],
      correspondenceImageUrl: outputs?['correspondence_image_url'],
      warnings: (json['warnings'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      failureReason: json['failure_reason'],
      transformationMatrix: matrix,
      configuration: json['configuration'],
    );
  }
}
