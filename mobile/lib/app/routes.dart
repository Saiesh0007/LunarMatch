import 'package:flutter/material.dart';
import '../screens/splash_screen.dart';
import '../screens/home_screen.dart';
import '../screens/upload_screen.dart';
import '../screens/configure_screen.dart';
import '../screens/processing_screen.dart';
import '../screens/results_screen.dart';
import '../screens/correspondence_screen.dart';
import '../screens/spatial_coverage_screen.dart';
import '../screens/robustness_screen.dart';
import '../screens/comparison_screen.dart';
import '../screens/failure_case_screen.dart';
import '../screens/status_screen.dart';
import '../screens/architecture_screen.dart';
import '../screens/about_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String home = '/home';
  static const String upload = '/upload';
  static const String configure = '/configure';
  static const String processing = '/processing';
  static const String results = '/results';
  static const String correspondence = '/correspondence';
  static const String spatialCoverage = '/spatial-coverage';
  static const String robustness = '/robustness';
  static const String comparison = '/comparison';
  static const String failureCase = '/failure-case';
  static const String status = '/status';
  static const String architecture = '/architecture';
  static const String about = '/about';

  static Map<String, WidgetBuilder> get routes => {
        splash: (context) => const SplashScreen(),
        home: (context) => const HomeScreen(),
        upload: (context) => const UploadScreen(),
        configure: (context) => const ConfigureScreen(),
        processing: (context) => const ProcessingScreen(),
        results: (context) => const ResultsScreen(),
        correspondence: (context) => const CorrespondenceScreen(),
        spatialCoverage: (context) => const SpatialCoverageScreen(),
        robustness: (context) => const RobustnessScreen(),
        comparison: (context) => const ComparisonScreen(),
        failureCase: (context) => const FailureCaseScreen(),
        status: (context) => const StatusScreen(),
        architecture: (context) => const ArchitectureScreen(),
        about: (context) => const AboutScreen(),
      };
}
