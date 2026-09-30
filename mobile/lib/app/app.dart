import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'theme.dart';
import 'routes.dart';
import '../providers/image_provider.dart';
import '../providers/pipeline_provider.dart';
import '../providers/experiment_provider.dart';

class LunarMatchApp extends StatelessWidget {
  const LunarMatchApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => LunarImageProvider()),
        ChangeNotifierProvider(create: (_) => PipelineProvider()),
        ChangeNotifierProvider(create: (_) => ExperimentProvider()),
      ],
      child: MaterialApp(
        title: 'LunarMatch',
        debugShowCheckedModeBanner: false,
        theme: LunarTheme.darkTheme,
        initialRoute: AppRoutes.splash,
        routes: AppRoutes.routes,
      ),
    );
  }
}
