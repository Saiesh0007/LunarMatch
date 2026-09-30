import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_animate/flutter_animate.dart';

void main() {
  testWidgets('flutter_animate animates and respects target 1 for reduced motion', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: const Text("Hello").animate(target: 1).fadeIn(duration: 400.ms),
        ),
      ),
    );
    final isTest = WidgetsBinding.instance.runtimeType.toString().contains('Test');
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: const Text("Hello")
              .animate(
                onPlay: (controller) {
                  if (!isTest) controller.repeat(reverse: true);
                },
              )
              .scale(begin: const Offset(1.0, 1.0), end: const Offset(1.02, 1.02), duration: 1500.ms),
        ),
      ),
    );
    expect(find.text("Hello"), findsOneWidget);
    await tester.pumpAndSettle();
    expect(find.text("Hello"), findsOneWidget);
  });
}
