import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/app.dart';

void main() {
  testWidgets('LunarMatchApp mounts cleanly and renders Splash Screen', (WidgetTester tester) async {
    await tester.pumpWidget(const LunarMatchApp());

    // Expect LunarMatch text on Splash Screen
    expect(find.text('LUNARMATCH'), findsOneWidget);
    expect(find.textContaining('SIH 2026'), findsOneWidget);
    expect(find.textContaining('ISRO'), findsOneWidget);

    // Advance past splash timer to Home Screen
    await tester.pump(const Duration(milliseconds: 2500));
    await tester.pumpAndSettle();

    // Verify Home Screen loaded cleanly
    expect(find.text('CORE CAPABILITIES'), findsOneWidget);
    expect(find.text('IMAGE REGISTRATION'), findsOneWidget);
  });
}
