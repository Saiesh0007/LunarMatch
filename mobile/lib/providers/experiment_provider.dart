import 'package:flutter/material.dart';
import '../models/experiment_model.dart';
import '../models/pipeline_model.dart';
import '../services/api_service.dart';

class ExperimentProvider with ChangeNotifier {
  String _experimentType = "illumination"; // illumination | scale | rotation | translation
  int _variationSteps = 5;
  double _minVal = -40.0;
  double _maxVal = 40.0;

  bool _isLoading = false;
  String? _errorMessage;
  RobustnessExperimentModel? _latestExperiment;

  String get experimentType => _experimentType;
  int get variationSteps => _variationSteps;
  double get minVal => _minVal;
  double get maxVal => _maxVal;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  RobustnessExperimentModel? get latestExperiment => _latestExperiment;

  void setExperimentType(String type) {
    _experimentType = type;
    if (type == "illumination") {
      _minVal = -50.0;
      _maxVal = 50.0;
    } else if (type == "scale") {
      _minVal = -20.0;
      _maxVal = 20.0;
    } else if (type == "rotation") {
      _minVal = -15.0;
      _maxVal = 15.0;
    } else if (type == "translation") {
      _minVal = -30.0;
      _maxVal = 30.0;
    }
    notifyListeners();
  }

  void setSteps(int steps) {
    _variationSteps = steps;
    notifyListeners();
  }

  void setRange(double min, double max) {
    _minVal = min;
    _maxVal = max;
    notifyListeners();
  }

  Future<void> runExperiment({
    required String baseImageId,
    required PipelineConfigModel config,
    bool isOffline = false,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    if (isOffline) {
      // Deterministic offline robustness curve simulator (Seed 26166)
      await Future.delayed(const Duration(milliseconds: 600));
      _latestExperiment = _generateOfflineExperiment(baseImageId);
      _isLoading = false;
      notifyListeners();
      return;
    }

    try {
      final res = await apiService.runRobustnessExperiment(
        baseImageId,
        _experimentType,
        _variationSteps,
        _minVal,
        _maxVal,
        config,
      );
      _latestExperiment = res;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  RobustnessExperimentModel _generateOfflineExperiment(String baseImageId) {
    final points = <RobustnessPointModel>[];
    final stepSize = (_maxVal - _minVal) / (_variationSteps - 1);

    for (int i = 0; i < _variationSteps; i++) {
      final val = _minVal + (i * stepSize);
      final distFromZero = (val / _maxVal).abs();

      // Realistic physical degradation: performance peaks near baseline (zero perturbation)
      final inliers = (85 * (1.0 - 0.65 * distFromZero)).round().clamp(6, 95);
      final inlierRatio = (72.0 * (1.0 - 0.55 * distFromZero)).clamp(8.0, 80.0);
      final coverage = (78.0 * (1.0 - 0.50 * distFromZero)).clamp(12.0, 82.0);
      final rmse = (1.2 + (distFromZero * 3.4));

      String lbl = val.toStringAsFixed(1);
      if (_experimentType == "illumination") lbl = "ΔB: ${val.toStringAsFixed(0)}";
      if (_experimentType == "scale") lbl = "Scale: ${(1.0 + val / 100).toStringAsFixed(2)}x";
      if (_experimentType == "rotation") lbl = "Rot: ${val.toStringAsFixed(1)}°";
      if (_experimentType == "translation") lbl = "Tx: ${val.toStringAsFixed(0)}px";

      points.add(
        RobustnessPointModel(
          variationValue: double.parse(val.toStringAsFixed(2)),
          variationLabel: lbl,
          inliers: inliers,
          inlierRatio: double.parse(inlierRatio.toStringAsFixed(1)),
          spatialCoverage: double.parse(coverage.toStringAsFixed(1)),
          rmsePx: inliers >= 8 ? double.parse(rmse.toStringAsFixed(2)) : null,
          runtimeMs: 145.0 + (i * 8.0),
          status: inliers >= 8 ? "SUCCESSFUL" : "NOT_RELIABLE",
        ),
      );
    }

    return RobustnessExperimentModel(
      experimentId: "offline_exp_seed26166",
      experimentType: _experimentType,
      baseImageId: baseImageId,
      disclaimer: "CONTROLLED SYNTHETIC EXPERIMENT — Deterministic profile simulation",
      points: points,
      summary: {
        "steps_completed": points.length,
        "peak_inliers": points.map((p) => p.inliers).reduce((a, b) => a > b ? a : b),
        "avg_inlier_ratio": 54.2,
        "avg_spatial_coverage": 61.8,
      },
    );
  }
}
