import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mobile/app/theme.dart';
import 'package:mobile/providers/image_provider.dart';
import 'package:mobile/providers/pipeline_provider.dart';
import 'package:mobile/providers/experiment_provider.dart';
import 'package:mobile/screens/home_screen.dart';
import 'package:mobile/screens/upload_screen.dart';
import 'package:mobile/screens/configure_screen.dart';
import 'package:mobile/screens/status_screen.dart';
import 'package:mobile/screens/architecture_screen.dart';
import 'package:mobile/screens/about_screen.dart';
import 'package:mobile/screens/robustness_screen.dart';
import 'package:mobile/screens/splash_screen.dart';
import 'package:mobile/screens/processing_screen.dart';
import 'package:mobile/screens/results_screen.dart';
import 'package:mobile/screens/correspondence_screen.dart';
import 'package:mobile/screens/spatial_coverage_screen.dart';
import 'package:mobile/screens/pipeline_details_screen.dart';

import 'package:mobile/models/pipeline_model.dart';
import 'package:mobile/models/metrics_model.dart';
import 'package:mobile/widgets/section_header.dart';
import 'package:mobile/widgets/metric_card.dart';

Widget _wrapWithProviders(
  Widget child, {
  Size screenSize = const Size(360, 640),
  PipelineProvider? pipelineProvider,
  LunarImageProvider? imageProvider,
  ExperimentProvider? experimentProvider,
}) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider(
        create: (_) => imageProvider ?? LunarImageProvider(),
      ),
      ChangeNotifierProvider(
        create: (_) => pipelineProvider ?? PipelineProvider(),
      ),
      ChangeNotifierProvider(
        create: (_) => experimentProvider ?? ExperimentProvider(),
      ),
    ],
    child: MaterialApp(
      theme: LunarTheme.darkTheme,
      home: MediaQuery(
        data: MediaQueryData(size: screenSize),
        child: child,
      ),
    ),
  );
}

void main() {
  group('Zero Overflow Tests on Narrow 360px Android Viewport', () {
    setUp(() {
      FlutterError.onError = (FlutterErrorDetails details) {
        FlutterError.dumpErrorToConsole(details, forceReport: true);
      };
    });

    testWidgets('HomeScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const HomeScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('LUNARMATCH'), findsOneWidget);
      expect(find.text('CORE CAPABILITIES'), findsOneWidget);
    });

    testWidgets('UploadScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const UploadScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('ConfigureScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const ConfigureScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('StatusScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const StatusScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('ENGINE CAPABILITIES'), findsOneWidget);
    });

    testWidgets('ArchitectureScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const ArchitectureScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('SYSTEM ARCHITECTURE'), findsOneWidget);
    });

    testWidgets('AboutScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const AboutScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('RobustnessScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const RobustnessScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('SplashScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const SplashScreen()));
      await tester.pump();

      expect(tester.takeException(), isNull);
      expect(find.text('LUNARMATCH'), findsOneWidget);
    });

    testWidgets('ProcessingScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const ProcessingScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets(
        'ResultsScreen renders without overflow when empty on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const ResultsScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets(
        'ResultsScreen populated with successful registration renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      final pipeProv = PipelineProvider();
      final res = PipelineRunResponseModel(
        runId: "test_success",
        status: "SUCCESSFUL",
        executionMode: "Offline",
        metrics: const RegistrationMetricsModel(
          metricMode: "DEMO",
          simulationSeed: 26166,
          keypointsReference: 1420,
          keypointsMoving: 1385,
          candidateMatches: 312,
          filteredMatches: 118,
          ransacInliers: 84,
          inlierRatio: 71.2,
          spatialCoverage: 77.8,
          spatialCoverageBefore: 38.9,
          rmsePx: 1.48,
          runtimeMs: 165.0,
          confidenceLevel: "HIGH",
          confidenceScore: 0.88,
          confidenceExplanation:
              "High-confidence registration with strong spatial distribution.",
        ),
        spatialStats: const SpatialStatsModel(
          gridSize: 6,
          totalCells: 36,
          occupiedBefore: 14,
          occupiedAfter: 28,
          coveragePercentageBefore: 38.9,
          coveragePercentageAfter: 77.8,
          coverageGainPercentage: 38.9,
        ),
        stages: [],
        warnings: [],
      );
      pipeProv.setLatestResponseForTesting(res);

      await tester.pumpWidget(
        _wrapWithProviders(const ResultsScreen(), pipelineProvider: pipeProv),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets(
        'ResultsScreen populated with rejected fail-safe renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      final pipeProv = PipelineProvider();
      final res = PipelineRunResponseModel(
        runId: "test_rejected",
        status: "REJECTED",
        executionMode: "Offline",
        metrics: const RegistrationMetricsModel(
          metricMode: "DEMO",
          simulationSeed: 26166,
          keypointsReference: 1420,
          keypointsMoving: 1385,
          candidateMatches: 312,
          filteredMatches: 118,
          ransacInliers: 4,
          inlierRatio: 3.4,
          spatialCoverage: 11.1,
          spatialCoverageBefore: 11.1,
          rmsePx: null,
          runtimeMs: 165.0,
          confidenceLevel: "REJECTED",
          confidenceScore: 0.0,
          confidenceExplanation:
              "REGISTRATION NOT RELIABLE: Insufficient inliers.",
        ),
        stages: [],
        warnings: ["Low inlier count detected"],
      );
      pipeProv.setLatestResponseForTesting(res);

      await tester.pumpWidget(
        _wrapWithProviders(const ResultsScreen(), pipelineProvider: pipeProv),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('CorrespondenceScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const CorrespondenceScreen()));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('SpatialCoverageScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        _wrapWithProviders(const SpatialCoverageScreen()),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('PipelineDetailsScreen renders without overflow on 360px viewport',
        (tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        _wrapWithProviders(const PipelineDetailsScreen()),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('SectionHeader never overflows on extremely narrow constraints',
        (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: LunarTheme.darkTheme,
          home: const Scaffold(
            body: Center(
              child: SizedBox(
                width: 80,
                child: SectionHeader(
                    title: "VERY LONG SECTION HEADER TEXT THAT SHOULD WRAP"),
              ),
            ),
          ),
        ),
      );
      await tester.pump();
      expect(tester.takeException(), isNull);
    });

    testWidgets('MetricCard handles long labels gracefully', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: LunarTheme.darkTheme,
          home: const Scaffold(
            body: Center(
              child: SizedBox(
                width: 120,
                child: MetricCard(
                  title: "TRANSFORMATION METRIC VALUE",
                  value: "0.1234 px",
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pump();
      expect(tester.takeException(), isNull);
    });
  });
}