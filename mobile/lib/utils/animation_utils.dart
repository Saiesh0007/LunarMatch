import 'package:flutter/material.dart';

/// Centralized animation utilities for LunarMatch
class AnimationUtils {
  /// Returns true if the user or OS has requested reduced motion.
  static bool isReducedMotion(BuildContext context) {
    return MediaQuery.maybeDisableAnimationsOf(context) ?? false;
  }

  /// Returns true if currently running within automated widget/unit tests.
  static bool get isRunningInTest {
    return WidgetsBinding.instance.runtimeType.toString().contains('Test');
  }

  /// Target value for flutter_animate: 1.0 (instantly complete) if reduced motion,
  /// otherwise null (plays normal animation).
  static double? targetFor(BuildContext context) {
    return isReducedMotion(context) ? 1.0 : null;
  }
}
