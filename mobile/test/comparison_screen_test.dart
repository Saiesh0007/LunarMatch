import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/screens/comparison_screen.dart';

void main() {
  group('ComparisonScreen', () {
    testWidgets('mounts and renders app bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: const ComparisonScreen(),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('Comparison'), findsOneWidget);
    });

    testWidgets('renders both columns with mock data', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: const ComparisonScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('SIFT'), findsWidgets);
      expect(find.textContaining('LUNARMATCH'), findsWidgets);
      expect(find.text('ACCEPTED'), findsWidgets);
    });

    testWidgets('has no overflow on phone viewport', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(375, 812);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: const ComparisonScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('has no overflow on desktop viewport', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1280, 720);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: const ComparisonScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });
  });
}