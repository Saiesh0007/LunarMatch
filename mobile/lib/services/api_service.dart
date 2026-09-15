import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/image_model.dart';
import '../models/pipeline_model.dart';
import '../models/experiment_model.dart';
import '../models/capability_model.dart';
import '../utils/constants.dart';

class ApiService {
  String _baseUrl;

  ApiService({String? baseUrl})
      : _baseUrl = baseUrl ?? _resolveDefaultBaseUrl();

  static String _resolveDefaultBaseUrl() {
    if (kIsWeb) return "http://127.0.0.1:8000";
    if (Platform.isAndroid) return AppConstants.defaultEmulatorApiUrl;
    return AppConstants.defaultLocalApiUrl;
  }

  String get baseUrl => _baseUrl;

  void setBaseUrl(String newUrl) {
    _baseUrl = newUrl.endsWith('/') ? newUrl.substring(0, newUrl.length - 1) : newUrl;
  }

  Future<bool> checkHealth() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/health'))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'ok';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<List<DemoPairModel>> fetchDemoPairs() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/v1/images/demo'))
        .timeout(const Duration(seconds: 4));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => DemoPairModel.fromJson(e)).toList();
    }
    throw Exception("Failed to fetch pairs: ${response.statusCode}");
  }

  Future<Map<String, dynamic>> uploadImageBytes(
      Uint8List bytes, String filename) async {
    final uri = Uri.parse('$_baseUrl/api/v1/images/upload');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      http.MultipartFile.fromBytes('file', bytes, filename: filename),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Upload failed: ${response.body}");
  }

  Future<PipelineRunResponseModel> runPipeline(
      String refId, String movId, String refSensor, String movSensor, PipelineConfigModel config) async {
    final body = {
      'reference_image_id': refId,
      'moving_image_id': movId,
      'reference_sensor': refSensor,
      'moving_sensor': movSensor,
      ...config.toJson(),
    };

    final response = await http
        .post(
          Uri.parse('$_baseUrl/api/v1/pipeline/run'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 45));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return PipelineRunResponseModel.fromJson(data);
    }
    throw Exception("Pipeline failed (${response.statusCode}): ${response.body}");
  }

  Future<RobustnessExperimentModel> runRobustnessExperiment(
      String baseImageId, String experimentType, int steps, double minVal, double maxVal, PipelineConfigModel config) async {
    final body = {
      'base_image_id': baseImageId,
      'experiment_type': experimentType,
      'variation_steps': steps,
      'min_val': minVal,
      'max_val': maxVal,
      'feature_method': config.featureMethod,
      'matcher': config.matcher,
      'ratio_threshold': config.ratioThreshold,
      'geometric_model': config.geometricModel,
      'spatial_balancing': config.spatialBalancing,
      'grid_size': config.gridSize,
    };

    final response = await http
        .post(
          Uri.parse('$_baseUrl/api/v1/experiments/robustness'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 60));

    if (response.statusCode == 200) {
      return RobustnessExperimentModel.fromJson(jsonDecode(response.body));
    }
    throw Exception("Experiment failed: ${response.body}");
  }

  Future<List<CapabilityItemModel>> fetchCapabilities() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/v1/capabilities'))
        .timeout(const Duration(seconds: 4));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = (data['capabilities'] as List<dynamic>?) ?? [];
      return list.map((e) => CapabilityItemModel.fromJson(e)).toList();
    }
    throw Exception("Failed to load capabilities");
  }

  Future<Map<String, dynamic>> fetchDemoCompare(String pairName) async {
    final response = await http
        .post(
          Uri.parse('$_baseUrl/api/demo/compare'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'pair_name': pairName}),
        )
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Compare failed (${response.statusCode}): ${response.body}");
  }

  Future<Map<String, dynamic>> fetchFailureCase() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/demo/failure-case'))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failure case fetch failed (${response.statusCode}): ${response.body}");
  }

  Future<Map<String, dynamic>> fetchRunResults(String runId) async {
    final uri = Uri.parse('/api/v1/results/');
    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Failed to fetch run results: ');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> fetchRunArtifact(String runId, String filename) async {
    final uri = Uri.parse('/api/v1/results//artifact/');
    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Failed to fetch artifact: ');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<String> fetchRunReport(String runId) async {
    final uri = Uri.parse('/api/v1/results//report');
    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Failed to fetch report: ');
    }
    return response.body;
  }

  String resolveFullUrl(String? endpointOrPath) {
    if (endpointOrPath == null) return "";
    if (endpointOrPath.isEmpty) return "";
    if (endpointOrPath.startsWith("http://") || endpointOrPath.startsWith("https://")) {
      return endpointOrPath;
    }
    if (!endpointOrPath.startsWith('/')) {
      return '$_baseUrl/$endpointOrPath';
    }
    return '$_baseUrl$endpointOrPath';
  }
}

final apiService = ApiService();
