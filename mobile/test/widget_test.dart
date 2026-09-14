import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/app.dart';

void main() {
  group('LunarMatchApp widget tests', () {
    testWidgets('LunarMatchApp mounts cleanly and renders Splash Screen', (WidgetTester tester) async {
      await tester.pumpWidget(const LunarMatchApp());

      expect(find.text('LUNARMATCH'), findsOneWidget);
      expect(find.text('SIH 2026'), findsOneWidget);
      expect(find.text('ISRO'), findsOneWidget);

      await tester.pump(const Duration(milliseconds: 2500));
      await tester.pumpAndSettle();

      expect(find.text('CORE CAPABILITIES'), findsOneWidget);
      expect(find.text('IMAGE REGISTRATION'), findsOneWidget);
    });

    testWidgets('HomeScreen navigates to comparison screen', (WidgetTester tester) async {
      await tester.pumpWidget(const LunarMatchApp());
      await tester.pump(const Duration(milliseconds: 2500));
      await tester.pumpAndSettle();

      expect(find.text('COMPARE SIFT vs LUNARMATCH'), findsOneWidget);
      await tester.tap(find.text('COMPARE SIFT vs LUNARMATCH'));
      await tester.pumpAndSettle();

      expect(find.text('SIFT vs LunarMatch'), findsOneWidget);
    });

    testWidgets('HomeScreen navigates to failure case screen', (WidgetTester tester) async {
      await tester.pumpWidget(const LunarMatchApp());
      await tester.pump(const Duration(milliseconds: 2500));
      await tester.pumpAndSettle();

      expect(find.text('SEE FAILURE DETECTION'), findsOneWidget);
      await tester.tap(find.text('SEE FAILURE DETECTION'));
      await tester.pumpAndSettle();

      expect(find.text('When LunarMatch Says NO'), findsOneWidget);
    });
  });
}
