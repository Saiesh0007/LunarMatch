import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/metrics_model.dart';
import 'package:mobile/models/match_model.dart';
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
  });
}
