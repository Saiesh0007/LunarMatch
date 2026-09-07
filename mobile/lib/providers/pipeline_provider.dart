import 'dart:async';
import 'package:flutter/material.dart';
import '../models/pipeline_model.dart';
import '../models/image_model.dart';
import '../services/api_service.dart';
import '../services/local_demo_simulator.dart';

enum PipelineExecutionStatus { idle, running, completed, error }

class PipelineProvider with ChangeNotifier {
  PipelineConfigModel _config = PipelineConfigModel();
  PipelineExecutionStatus _status = PipelineExecutionStatus.idle;
  
  bool _isBackendConnected = false;
  bool _forceLocalDemo = false;

  PipelineRunResponseModel? _latestResponse;
  List<PipelineStageModel> _currentStages = [];
  String? _errorMessage;

  PipelineConfigModel get config => _config;
  PipelineExecutionStatus get status => _status;
  bool get isBackendConnected => _isBackendConnected;
  bool get forceLocalDemo => _forceLocalDemo;
  PipelineRunResponseModel? get latestResponse => _latestResponse;
  List<PipelineStageModel> get currentStages => _currentStages;
  String? get errorMessage => _errorMessage;

  String get currentExecutionModeLabel {
    if (_forceLocalDemo || !_isBackendConnected) {
      return "LOCAL DEMO";
    }
    if (_config.simulationMode || _config.featureMethod != "SIFT") {
      return "SIMULATED PIPELINE";
    }
    return "LIVE BASELINE";
  }

  PipelineProvider() {
    checkBackendHealth();
  }

  Future<void> checkBackendHealth() async {
    _isBackendConnected = await apiService.checkHealth();
    notifyListeners();
  }

  void toggleLocalDemoMode(bool enable) {
    _forceLocalDemo = enable;
    notifyListeners();
  }

  void updateConfig(PipelineConfigModel newConfig) {
    _config = newConfig;
    notifyListeners();
  }

  void resetConfig() {
    _config = PipelineConfigModel();
    notifyListeners();
  }

  void setLatestResponseForTesting(PipelineRunResponseModel res) {
    _latestResponse = res;
    _status = PipelineExecutionStatus.completed;
    notifyListeners();
  }

  Future<void> runRegistration({
    required LunarImageModel refImage,
    required LunarImageModel movImage,
    required String refSensor,
    required String movSensor,
    String? pairId,
  }) async {
    _status = PipelineExecutionStatus.running;
    _errorMessage = null;
    _currentStages = _initializeStages();
    notifyListeners();

    // Check if we must use local demo simulator
    final mustUseLocal = _forceLocalDemo || !_isBackendConnected || refImage.isAsset;

    if (mustUseLocal) {
      try {
        final res = await LocalDemoSimulator.simulateDemoRun(
          pairId: pairId ?? "pair_a",
          config: _config,
          onStageUpdate: (stage) {
            final idx = _currentStages.indexWhere((s) => s.stageNumber == stage.stageNumber);
            if (idx != -1) {
              _currentStages[idx] = stage;
              notifyListeners();
            }
          },
        );
        _latestResponse = res;
        _status = PipelineExecutionStatus.completed;
        notifyListeners();
        return;
      } catch (e) {
        _errorMessage = "Local demo simulator failure: $e";
        _status = PipelineExecutionStatus.error;
        notifyListeners();
        return;
      }
    }

    // Otherwise, call FastAPI live/simulated pipeline
    try {
      // Stream simulated progress while backend computes
      Timer? progressTimer;
      int step = 0;
      progressTimer = Timer.periodic(const Duration(milliseconds: 180), (timer) {
        if (step < _currentStages.length) {
          _currentStages[step].status = "PROCESSING";
          if (step > 0) {
            _currentStages[step - 1].status = "COMPLETED";
          }
          step++;
          notifyListeners();
        } else {
          timer.cancel();
        }
      });

      final response = await apiService.runPipeline(
        refImage.id,
        movImage.id,
        refSensor,
        movSensor,
        _config,
      );

      progressTimer.cancel();
      _latestResponse = response;
      _currentStages = response.stages;
      _status = PipelineExecutionStatus.completed;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _status = PipelineExecutionStatus.error;
      notifyListeners();
    }
  }

  List<PipelineStageModel> _initializeStages() {
    return [
      PipelineStageModel(stageNumber: 1, name: "INPUT VALIDATION"),
      PipelineStageModel(stageNumber: 2, name: "PREPROCESSING"),
      PipelineStageModel(stageNumber: 3, name: "FEATURE EXTRACTION"),
      PipelineStageModel(stageNumber: 4, name: "FEATURE MATCHING"),
      PipelineStageModel(stageNumber: 5, name: "RATIO FILTERING"),
      PipelineStageModel(stageNumber: 6, name: "GEOMETRIC VERIFICATION"),
      PipelineStageModel(stageNumber: 7, name: "SPATIAL BALANCING"),
      PipelineStageModel(stageNumber: 8, name: "TRANSFORMATION"),
      PipelineStageModel(stageNumber: 9, name: "REGISTRATION"),
      PipelineStageModel(stageNumber: 10, name: "METRICS"),
    ];
  }
}
