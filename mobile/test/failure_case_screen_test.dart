import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mobile/screens/failure_case_screen.dart';

import 'comparison_screen_test.mocks.dart';

const fakeFailureCase = {
  "decision": "REGISTRATION_NOT_RELIABLE",
  "reason": "Failed criteria: inlier_count, inlier_ratio, spatial_coverage, rmse_pixels, homography_determinant, condition_number_H",
  "failed_criteria": ["inlier_count", "inlier_ratio", "spatial_coverage", "rmse_pixels", "homography_determinant", "condition_number_H"],
  "criteria": [
    {
      "name": "overlap_ratio",
      "label": "Overlap ratio",
      "value": 1.0,
      "threshold": 0.1,
      "pass": true,
      "display": "1.00",
    },
    {
      "name": "inlier_count",
      "label": "Inlier count",
      "value": 0.0,
      "threshold": 30,
      "pass": false,
      "display": "0",
    },
    {
      "name": "inlier_ratio",
      "label": "Inlier ratio",
      "value": 0.0,
      "threshold": 0.15,
      "pass": false,
      "display": "0.00",
    },
    {
      "name": "spatial_coverage",
      "label": "Spatial coverage",
      "value": 0.0,
      "threshold": 0.4,
      "pass": false,
      "display": "0.00",
    },
    {
      "name": "rmse_pixels",
      "label": "RMSE",
      "value": null,
      "threshold": 2.0,
      "pass": false,
      "display": "N/A px",
    },
    {
      "name": "homography_determinant",
      "label": "Determinant",
      "value": null,
      "threshold": [0.5, 2.0],
      "pass": false,
      "display": "N/A",
    },
    {
      "name": "condition_number_H",
      "label": "Condition number",
      "value": null,
      "threshold": 1000000.0,
      "pass": false,
      "display": "N/A",
    },
  ],
  "n_inliers": 0,
  "n_rejected_refinement": 0,
  "note": "We return REGISTRATION_NOT_RELIABLE rather than a wrong transform. Downstream users can trust the metric.",
};

void main() {
  group('FailureCaseScreen', () {
    testWidgets('mounts and renders app bar', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchFailureCase()).thenAnswer((_) async => fakeFailureCase);

      await tester.pumpWidget(
        MaterialApp(
          theme:ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: FailureCaseScreen(apiClient: mock),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('When LunarMatch Says NO'), findsOneWidget);
    });

    testWidgets('renders checklist and reason after settling', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchFailureCase()).thenAnswer((_) async => fakeFailureCase);

      await tester.pumpWidget(
        MaterialApp(
          theme:ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: FailureCaseScreen(apiClient: mock),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('When LunarMatch Says NO'), findsOneWidget);
      expect(find.text('ACCEPTANCE CRITERIA'), findsOneWidget);
      expect(find.text('REGISTRATION_NOT_RELIABLE'), findsOneWidget);
      expect(find.text('FAIL'), findsWidgets);
      expect(find.text('RMSE'), findsOneWidget);
    });

    testWidgets('shows error state on API failure', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchFailureCase()).thenAnswer((_) => Future.error(Exception('500')));

      await tester.pumpWidget(
        MaterialApp(
          theme:ThemeData.dark(),
          home: FailureCaseScreen(apiClient: mock),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Error'), findsOneWidget);
    });

    testWidgets('has no overflow on phone viewport', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(375, 812);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      final mock = MockApiService();
      when(mock.fetchFailureCase()).thenAnswer((_) async => fakeFailureCase);

      await tester.pumpWidget(
        MaterialApp(
          theme:ThemeData.dark(),
          home: FailureCaseScreen(apiClient: mock),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('has no overflow on desktop viewport', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1280, 720);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      final mock = MockApiService();
      when(mock.fetchFailureCase()).thenAnswer((_) async => fakeFailureCase);

      await tester.pumpWidget(
        MaterialApp(
          theme:ThemeData.dark(),
          home: FailureCaseScreen(apiClient: mock),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });
  });
}