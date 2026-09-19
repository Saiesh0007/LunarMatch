import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/metrics_model.dart';
import 'package:mobile/models/match_model.dart';
import 'package:mobile/models/pipeline_model.dart';
import 'package:mobile/utils/formatters.dart';

void main() {
  group('LunarMatch Frontend Models', () {
    test('RegistrationMetricsModel deserializes correctly', () {
      final json = {
        'metric_mode': 'MEASURED',
        'keypoints_reference': 1200,
        'keypoints_moving': 1150,
        'candidate_matches': 280,
        'filtered_matches': 95,
        'ransac_inliers': 72,
        'inlier_ratio': 75.8,
        'spatial_coverage': 68.5,
        'spatial_coverage_before': 33.3,
        'rmse_px': 1.42,
        'runtime_ms': 135.5,
        'confidence_level': 'HIGH',
        'confidence_score': 0.85,
        'confidence_explanation': 'Test explanation',
      };

      final m = RegistrationMetricsModel.fromJson(json);
      expect(m.metricMode, 'MEASURED');
      expect(m.keypointsReference, 1200);
      expect(m.ransacInliers, 72);
      expect(m.rmsePx, 1.42);
      expect(m.confidenceLevel, 'HIGH');
    });

    test('MatchPairModel parses and handles coordinates', () {
      final json = {
        'ref_idx': 1,
        'mov_idx': 1,
        'distance': 45.2,
        'ref_pt': [120.5, 230.0],
        'mov_pt': [125.0, 235.5],
        'is_inlier': true,
        'is_spatially_selected': true,
      };

      final pair = MatchPairModel.fromJson(json);
      expect(pair.refIdx, 1);
      expect(pair.distance, 45.2);
      expect(pair.refPt, [120.5, 230.0]);
      expect(pair.isInlier, true);
    });

    test('Formatters return formatted strings or N/A', () {
      expect(Formatters.formatPixels(1.234), '1.23 px');
      expect(Formatters.formatPixels(null), 'N/A');
      expect(Formatters.formatPercentage(84.22), '84.2%');
      expect(Formatters.formatPercentage(null), 'N/A');
    });

    test('rmse_px parsed from flat response', () {
      final json = {
        'run_id': 'test',
        'rmse_px': 0.592,
        'keypoints_ref': 1430,
        'inliers': 22,
      };
      final model = PipelineRunResponseModel.fromJson(json);
      expect(model.metrics.rmsePx, 0.592);
    });

    test('rmse_px parsed from nested response', () {
      final json = {
        'run_id': 'test',
        'metrics': {'rmse_px': 0.592},
      };
      final model = PipelineRunResponseModel.fromJson(json);
      expect(model.metrics.rmsePx, 0.592);
    });

    test('StageDetailModel parses reserved fields and maps extras correctly', () {
      final json = {
        'stage': 'crs',
        'ms': 428.04,
        'fallback': false,
        'reason': 'All tests passed',
        'overlap_ratio': 0.89,
        'custom_metric': 123,
      };
      final model = StageDetailModel.fromJson(json);
      expect(model.stage, 'crs');
      expect(model.ms, 428.04);
      expect(model.fallback, false);
      expect(model.reason, 'All tests passed');
      expect(model.extras['overlap_ratio'], 0.89);
      expect(model.extras['custom_metric'], 123);
      expect(model.extras.containsKey('stage'), false);
      expect(model.extras.containsKey('ms'), false);
    });

    test('MatcherBenchmarkModel parses matchers with active and skipped entries', () {
      final json = {
        'pairs_tested': 2,
        'timestamp': '2026-09-18T05:20:28Z',
        'matchers': [
          {
            'name': 'RIFT2 + BF',
            'success_rate': 1.0,
            'mean_rmse_px': 0.65,
            'mean_time_ms': 14477.8,
            'notes': 'Shipped (live)',
          },
          {
            'name': 'SuperGlue',
            'skipped': true,
            'reason': 'weight file not found',
          }
        ]
      };
      final model = MatcherBenchmarkModel.fromJson(json);
      expect(model.pairsTested, 2);
      expect(model.timestamp, '2026-09-18T05:20:28Z');
      expect(model.matchers.length, 2);

      final rift = model.matchers[0];
      expect(rift.name, 'RIFT2 + BF');
      expect(rift.successRate, 1.0);
      expect(rift.meanRmsePx, 0.65);
      expect(rift.meanTimeMs, 14477.8);
      expect(rift.skipped, false);

      final sg = model.matchers[1];
      expect(sg.name, 'SuperGlue');
      expect(sg.skipped, true);
      expect(sg.reason, 'weight file not found');
    });

    test('PipelineConfigModel defaults to RIFT2 and BF', () {
      final cfg = PipelineConfigModel();
      expect(cfg.featureMethod, 'RIFT2');
      expect(cfg.matcher, 'BF');
    });
  });
}
