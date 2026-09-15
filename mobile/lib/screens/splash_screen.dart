import 'dart:async';
import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../app/routes.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _progressAnim;
  Timer? _navTimer;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2500),
    );
    _progressAnim = CurvedAnimation(parent: _animController, curve: Curves.easeInOut);
    _animController.forward();

    _navTimer = Timer(const Duration(milliseconds: 2500), () {
      if (mounted) {
        Navigator.pushReplacementNamed(context, AppRoutes.home);
      }
    });
  }

  @override
  void dispose() {
    _navTimer?.cancel();
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      body: SafeArea(
        child: AnimatedBuilder(
          animation: _progressAnim,
          builder: (context, child) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo
                    Image.asset(
                      'assets/images/logo.png',
                      width: 200,
                      height: 200,
                      fit: BoxFit.contain,
                    ),
                    const SizedBox(height: 24),

                    // App Title
                    const Text(
                      "LunarMatch",
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.w800,
                        color: LunarTheme.primary,
                      ),
                    ),
                    const SizedBox(height: 8),

                    // Subtitle
                    const Text(
                      "Multi-Modal Lunar Registration",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: LunarTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 48),

                    // Bottom meta row
                    Wrap(
                      alignment: WrapAlignment.center,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 16,
                      children: [
                        Text(
                          "ISRO SIH 2026 · PS 26166",
                          style: LunarTheme.mono.copyWith(
                            fontSize: 11,
                            color: LunarTheme.textTertiary,
                          ),
                        ),
                        Text(
                          "For a Brighter Bharat",
                          style: LunarTheme.mono.copyWith(
                            fontSize: 11,
                            color: LunarTheme.primary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),

                    // Thin saffron progress ring
                    SizedBox(
                      width: 48,
                      height: 48,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          CircularProgressIndicator(
                            value: _progressAnim.value,
                            strokeWidth: 2,
                            backgroundColor: LunarTheme.borderLight,
                            valueColor: const AlwaysStoppedAnimation<Color>(LunarTheme.primary),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
