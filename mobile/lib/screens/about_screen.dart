import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../providers/pipeline_provider.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("About"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Centered logo
              Image.asset(
                'assets/images/logo.png',
                width: 120,
                height: 120,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 16),

              // App name
              const Text(
                "LunarMatch",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: LunarTheme.primary,
                ),
              ),
              const SizedBox(height: 8),

              // Tagline
              Text(
                "Multi-Modal Lunar Registration Engine",
                style: const TextStyle(
                  fontSize: 14,
                  color: LunarTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 24),

              // 3 badges
              Wrap(
                alignment: WrapAlignment.center,
                spacing: 12,
                runSpacing: 12,
                children: [
                  _buildBadge("ISRO SIH 2026", LunarTheme.primary),
                  _buildBadge("PS 26166", LunarTheme.success),
                  _buildBadge("v1.0.0", LunarTheme.textTertiary),
                ],
              ),
              const SizedBox(height: 32),

              // Credits panel
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "CREDITS",
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                        color: LunarTheme.textTertiary,
                      ),
                    ),
                    const SizedBox(height: 16),
                    _buildCreditRow("Developed by", "Team LunarMatch"),
                    _buildCreditRow("For", "Smart India Hackathon 2026"),
                    _buildCreditRow("Problem Statement", "PS 26166"),
                    _buildCreditRow("Domain", "Space Technology / Lunar Imaging"),
                    _buildCreditRow("Backend", "FastAPI + OpenCV (Python)"),
                    _buildCreditRow("Frontend", "Flutter (Dart)"),
                    const SizedBox(height: 16),
                    const Divider(height: 1, color: LunarTheme.border),
                    const SizedBox(height: 16),
                    _buildCreditRow("Algorithms", "SIFT, RIFT2, MAGSAC++, FLANN"),
                    _buildCreditRow("Libraries", "OpenCV, NumPy, SciPy, fl_chart"),
                    _buildCreditRow("Demo Data", "Procedural lunar terrain synthesis"),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // Footer
              Column(
                children: [
                  Text(
                    "For a Brighter Bharat",
                    style: LunarTheme.mono.copyWith(
                      fontSize: 11,
                      color: LunarTheme.primary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "LunarMatch is a research prototype. Not for flight use.",
                    style: LunarTheme.mono.copyWith(
                      fontSize: 9,
                      color: LunarTheme.textTertiary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color, width: 1),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }

  Widget _buildCreditRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: LunarTheme.textTertiary),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: LunarTheme.textPrimary),
            ),
          ),
        ],
      ),
    );
  }
}