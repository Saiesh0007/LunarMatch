import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mobile/screens/comparison_screen.dart';

import 'comparison_screen_test.mocks.dart';

const fakeComparisonResult = {
  "pair_name": "Pair A: bundled prototype",
  "provenance": "REAL MEASURED — both SIFT and LunarMatch RIFT2 run through the full pipeline on the same pair",
  "sift": {
    "status": "SUCCESSFUL",
    "inliers": 1393,
    "rmse_px": 0.461,
    "coverage": 1.0,
    "inlier_ratio": 1.0,
    "decision": "ACCEPTED",
  },
  "lunarmatch": {
    "status": "NOT_RELIABLE",
    "inliers": 0,
    "rmse_px": null,
    "coverage": 0.0,
    "inlier_ratio": 0.0,
    "decision": "REGISTRATION_NOT_RELIABLE",
  },
};

void main() {
  group('ComparisonScreen', () {
    testWidgets('mounts and renders app bar', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchDemoCompare('Pair A: bundled prototype')).thenAnswer((_) async => fakeComparisonResult);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: ComparisonScreen(apiClient: mock),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('SIFT vs LunarMatch'), findsOneWidget);
    });

    testWidgets('renders both columns with real measured data', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchDemoCompare('Pair A: bundled prototype')).thenAnswer((_) async => fakeComparisonResult);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: ComparisonScreen(apiClient: mock),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('SIFT'), findsWidgets);
      expect(find.textContaining('LunarMatch'), findsWidgets);
      // SIFT succeeds on Pair A (real result, not fabricated)
      expect(find.text('ACCEPTED'), findsWidgets);
      // LunarMatch fails on Pair A (0 inliers, NOT_RELIABLE)
      expect(find.text('REJECTED'), findsOneWidget);
      expect(find.text('1393'), findsOneWidget);
      // Delta card shows LunarMatch trailing SIFT
      expect(find.textContaining('inliers'), findsWidgets);
    });

    testWidgets('shows error state on API failure', (WidgetTester tester) async {
      final mock = MockApiService();
      when(mock.fetchDemoCompare('Pair A: bundled prototype')).thenAnswer((_) => Future.error(Exception('500')));

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: ComparisonScreen(apiClient: mock),
          ),
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
      when(mock.fetchDemoCompare('Pair A: bundled prototype')).thenAnswer((_) async => fakeComparisonResult);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: ComparisonScreen(apiClient: mock),
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
      when(mock.fetchDemoCompare('Pair A: bundled prototype')).thenAnswer((_) async => fakeComparisonResult);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: ComparisonScreen(apiClient: mock),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });
  });
}
