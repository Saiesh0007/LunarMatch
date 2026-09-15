import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/screens/failure_case_screen.dart';

void main() {
  group('FailureCaseScreen', () {
    testWidgets('mounts and renders app bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: const FailureCaseScreen(),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('Failure Case'), findsOneWidget);
    });

    testWidgets('renders checklist and reason after settling', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1280, 720)),
            child: const FailureCaseScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Registration Not Reliable'), findsOneWidget);
      expect(find.text('ACCEPTANCE CRITERIA'), findsOneWidget);
      expect(find.text('REGISTRATION_NOT_RELIABLE'), findsOneWidget);
      expect(find.text('FAIL'), findsWidgets);
      expect(find.text('Inlier Ratio ≥ 0.4'), findsOneWidget);
    });

    testWidgets('has no overflow on phone viewport', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(375, 812);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: const FailureCaseScreen(),
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
          home: const FailureCaseScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });
  });
}