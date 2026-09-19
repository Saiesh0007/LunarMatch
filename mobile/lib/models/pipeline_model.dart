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
  String featureMethod;
  String matcher;
  double ratioThreshold;
  String geometricModel;
  String estimatorMethod;
  bool subpixelRefinement;
  int subpixelPatchSize;
  double subpixelPeakThreshold;
  bool spatialBalancing;
  int gridSize;
  int maxPerCell;
  double ransacThreshold;
  int maxFeatures;
  PreprocessingConfigModel preprocessing;
  bool simulationMode;
  bool failSafeOverride;

  PipelineConfigModel({
    this.featureMethod = "RIFT2",
    this.matcher = "BF",
    this.ratioThreshold = 0.75,
    this.geometricModel = "homography",
    this.estimatorMethod = "magsac",
    this.subpixelRefinement = true,
    this.subpixelPatchSize = 64,
    this.subpixelPeakThreshold = 0.2,
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
    'estimator_method': estimatorMethod,
    'subpixel_refinement': subpixelRefinement,
    'subpixel_patch_size': subpixelPatchSize,
    'subpixel_peak_threshold': subpixelPeakThreshold,
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
  String status;
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

class SubpixelDiagnosticsModel {
  final bool enabled;
  final int patchSize;
  final double peakResponseThreshold;
  final int nRefined;
  final int nRejectedRefinement;
  final int nRejectedOutOfBounds;
  final double? meanResidualPx;
  final double? medianResidualPx;
  final double? p95ResidualPx;

  const SubpixelDiagnosticsModel({
    required this.enabled,
    required this.patchSize,
    required this.peakResponseThreshold,
    required this.nRefined,
    required this.nRejectedRefinement,
    required this.nRejectedOutOfBounds,
    this.meanResidualPx,
    this.medianResidualPx,
    this.p95ResidualPx,
  });

  factory SubpixelDiagnosticsModel.fromJson(Map<String, dynamic> json) {
    return SubpixelDiagnosticsModel(
      enabled: json['enabled'] as bool? ?? false,
      patchSize: json['patch_size'] as int? ?? 64,
      peakResponseThreshold: (json['peak_response_threshold'] as num?)?.toDouble() ?? 0.2,
      nRefined: json['n_refined'] as int? ?? 0,
      nRejectedRefinement: json['n_rejected_refinement'] as int? ?? 0,
      nRejectedOutOfBounds: json['n_rejected_out_of_bounds'] as int? ?? 0,
      meanResidualPx: (json['mean_residual_px'] as num?)?.toDouble(),
      medianResidualPx: (json['median_residual_px'] as num?)?.toDouble(),
      p95ResidualPx: (json['p95_residual_px'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'enabled': enabled,
    'patch_size': patchSize,
    'peak_response_threshold': peakResponseThreshold,
    'n_refined': nRefined,
    'n_rejected_refinement': nRejectedRefinement,
    'n_rejected_out_of_bounds': nRejectedOutOfBounds,
    if (meanResidualPx != null) 'mean_residual_px': meanResidualPx,
    if (medianResidualPx != null) 'median_residual_px': medianResidualPx,
    if (p95ResidualPx != null) 'p95_residual_px': p95ResidualPx,
  };
}

class RegistrationDecisionModel {
  final String decision;
  final String reason;
  final Map<String, dynamic> checklist;
  final List<String> failedCriteria;

  const RegistrationDecisionModel({
    required this.decision,
    required this.reason,
    required this.checklist,
    required this.failedCriteria,
  });

  factory RegistrationDecisionModel.fromJson(Map<String, dynamic> json) {
    return RegistrationDecisionModel(
      decision: json['decision'] as String? ?? 'UNKNOWN',
      reason: json['reason'] as String? ?? '',
      checklist: (json['checklist'] as Map<String, dynamic>?) ?? {},
      failedCriteria: (json['failed_criteria'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
    'decision': decision,
    'reason': reason,
    'checklist': checklist,
    'failed_criteria': failedCriteria,
  };
}

class RoutingConfigModel {
  final String sourceSensor;
  final String referenceSensor;
  final String featureMethod;
  final String matcher;
  final String estimator;
  final String geometryModel;
  final bool subpixelRefinement;
  final int pyramidLevels;
  final String rationale;

  const RoutingConfigModel({
    required this.sourceSensor,
    required this.referenceSensor,
    required this.featureMethod,
    required this.matcher,
    required this.estimator,
    required this.geometryModel,
    required this.subpixelRefinement,
    required this.pyramidLevels,
    required this.rationale,
  });

  factory RoutingConfigModel.fromJson(Map<String, dynamic> json) {
    return RoutingConfigModel(
      sourceSensor: json['source_sensor'] as String? ?? '',
      referenceSensor: json['reference_sensor'] as String? ?? '',
      featureMethod: json['feature_method'] as String? ?? '',
      matcher: json['matcher'] as String? ?? '',
      estimator: json['estimator'] as String? ?? '',
      geometryModel: json['geometry_model'] as String? ?? '',
      subpixelRefinement: json['subpixel_refinement'] as bool? ?? false,
      pyramidLevels: json['pyramid_levels'] as int? ?? 1,
      rationale: json['rationale'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'source_sensor': sourceSensor,
    'reference_sensor': referenceSensor,
    'feature_method': featureMethod,
    'matcher': matcher,
    'estimator': estimator,
    'geometry_model': geometryModel,
    'subpixel_refinement': subpixelRefinement,
    'pyramid_levels': pyramidLevels,
    'rationale': rationale,
  };
}

class PipelineRunResponseModel {
  final String runId;
  final String status;
  final String executionMode;
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
  final SubpixelDiagnosticsModel? subpixelDiagnostics;
  final RegistrationDecisionModel? registrationDecision;
  final RoutingConfigModel? routingConfig;
  final Map<String, dynamic>? diagnosticDetails;

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
    this.subpixelDiagnostics,
    this.registrationDecision,
    this.routingConfig,
    this.diagnosticDetails,
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

    final diag = json['diagnostic_details'] as Map<String, dynamic>?;
    final subpixelRaw = json['subpixel_diagnostics'] as Map<String, dynamic>? ??
        diag?['subpixel_diagnostics'] as Map<String, dynamic>? ??
        diag?['subpixel'] as Map<String, dynamic>?;
    final regRaw = json['registration_decision'] as Map<String, dynamic>? ??
        diag?['registration_decision'] as Map<String, dynamic>?;
    final routingRaw = json['routing_config'] as Map<String, dynamic>? ??
        diag?['routing_config'] as Map<String, dynamic>? ??
        diag?['routing'] as Map<String, dynamic>?;

    return PipelineRunResponseModel(
      runId: json['run_id'] ?? '',
      status: json['status'] ?? 'FAILED',
      executionMode: json['execution_mode'] ?? 'LIVE',
      stages: stagesList,
      metrics: RegistrationMetricsModel.fromJson(
        json['metrics'] as Map<String, dynamic>? ?? json,
      ),
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
      subpixelDiagnostics: subpixelRaw != null ? SubpixelDiagnosticsModel.fromJson(subpixelRaw) : null,
      registrationDecision: regRaw != null ? RegistrationDecisionModel.fromJson(regRaw) : null,
      routingConfig: routingRaw != null ? RoutingConfigModel.fromJson(routingRaw) : null,
      diagnosticDetails: diag,
    );
  }
}

/// A single stage-level entry from match_decisions.jsonl.
/// Uses an [extras] map for stage-specific fields to keep the schema
/// stable as new stages or fields are added upstream.
class StageDetailModel {
  final String stage;
  final double? ms;
  final bool? fallback;
  final String? reason;
  final Map<String, dynamic> extras;

  const StageDetailModel({
    required this.stage,
    this.ms,
    this.fallback,
    this.reason,
    this.extras = const {},
  });

  factory StageDetailModel.fromJson(Map<String, dynamic> json) {
    const reserved = {'stage', 'ms', 'fallback', 'reason'};
    return StageDetailModel(
      stage: json['stage'] as String? ?? '',
      ms: (json['ms'] as num?)?.toDouble(),
      fallback: json['fallback'] as bool?,
      reason: json['reason'] as String?,
      extras: Map<String, dynamic>.fromEntries(
        json.entries.where((e) => !reserved.contains(e.key)),
      ),
    );
  }

  /// Whether this stage passed (true), failed (false), or is unknown (null).
  bool? get ok => extras['ok'] as bool?;
}

/// Benchmark comparison between matchers (read from matcher_benchmark.json).
class MatcherBenchmarkModel {
  final int pairsTested;
  final String timestamp;
  final List<MatcherResultModel> matchers;

  const MatcherBenchmarkModel({
    required this.pairsTested,
    required this.timestamp,
    required this.matchers,
  });

  factory MatcherBenchmarkModel.fromJson(Map<String, dynamic> json) {
    return MatcherBenchmarkModel(
      pairsTested: json['pairs_tested'] as int? ?? 0,
      timestamp: json['timestamp'] as String? ?? '',
      matchers: (json['matchers'] as List<dynamic>?)
              ?.map((e) => MatcherResultModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

/// Individual matcher result within a benchmark comparison.
class MatcherResultModel {
  final String name;
  final double? successRate;
  final double? meanRmsePx;
  final double? meanTimeMs;
  final String? notes;
  final bool skipped;
  final String? reason;

  const MatcherResultModel({
    required this.name,
    this.successRate,
    this.meanRmsePx,
    this.meanTimeMs,
    this.notes,
    this.skipped = false,
    this.reason,
  });

  factory MatcherResultModel.fromJson(Map<String, dynamic> json) {
    return MatcherResultModel(
      name: json['name'] as String? ?? '',
      successRate: (json['success_rate'] as num?)?.toDouble(),
      meanRmsePx: (json['mean_rmse_px'] as num?)?.toDouble(),
      meanTimeMs: (json['mean_time_ms'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      skipped: json['skipped'] as bool? ?? false,
      reason: json['reason'] as String?,
    );
  }
}

