import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mobile/app/theme.dart';
import 'package:mobile/providers/image_provider.dart';
import 'package:mobile/providers/pipeline_provider.dart';
import 'package:mobile/providers/experiment_provider.dart';
import 'package:mobile/screens/home_screen.dart';

Widget _wrapWithProviders(Widget child) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider(create: (_) => LunarImageProvider()),
      ChangeNotifierProvider(create: (_) => PipelineProvider()),
      ChangeNotifierProvider(create: (_) => ExperimentProvider()),
    ],
    child: MaterialApp(
      theme: LunarTheme.darkTheme,
      home: child,
    ),
  );
}

void main() {
  group('LunarMatchApp widget tests', () {
    testWidgets('HomeScreen mounts cleanly', (WidgetTester tester) async {
      await tester.pumpWidget(_wrapWithProviders(const HomeScreen()));
      await tester.pump();

      expect(tester.takeException(), isNull);
      expect(find.text('LUNARMATCH'), findsOneWidget);
      expect(find.text('CORE CAPABILITIES'), findsOneWidget);
    });

    testWidgets('HomeScreen shows all four dashboard cards',
        (WidgetTester tester) async {
      await tester.pumpWidget(_wrapWithProviders(const HomeScreen()));
      await tester.pump();

      expect(find.text('Image Registration'), findsOneWidget);
      expect(find.text('Robustness Lab'), findsOneWidget);
      expect(find.text('Engine Capabilities'), findsOneWidget);
      expect(find.text('Pipeline Architecture'), findsOneWidget);
    });

    testWidgets('HomeScreen has bottom navigation',
        (WidgetTester tester) async {
      await tester.pumpWidget(_wrapWithProviders(const HomeScreen()));
      await tester.pump();

      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Register'), findsOneWidget);
      expect(find.text('Lab'), findsOneWidget);
      expect(find.text('About'), findsOneWidget);
    });

    testWidgets('HomeScreen does not overflow on narrow viewport',
        (WidgetTester tester) async {
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_wrapWithProviders(const HomeScreen()));
      await tester.pump();

      expect(tester.takeException(), isNull);
    });
  });
}