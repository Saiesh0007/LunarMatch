import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../app/theme.dart';
import '../utils/animation_utils.dart';

class ArchitectureScreen extends StatelessWidget {
  const ArchitectureScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final animTarget = AnimationUtils.targetFor(context);

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("SYSTEM ARCHITECTURE"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Overview Banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "PIPELINE SPECIFICATION",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      "Multi-stage phase-congruency and robust-estimation pipeline "
                      "engineered for extreme multi-modal radiometric and geometric "
                      "correspondence between OHRC, TMC-2, IIRS optical imagery and "
                      "LRO NAC reference imagery.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.45),
                    ),
                  ],
                ),
              )
                  .animate(target: animTarget)
                  .fadeIn(duration: 400.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Pipeline stages
              ..._buildPipeline(context, animTarget),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildPipeline(BuildContext context, double? animTarget) {
    final stages = [
      (
        "01",
        "MULTI-MODAL INGESTION & LUNAR CRS",
        "PDS4 metadata parsing, SPICE kernel loading (IK / FK / SPK), "
            "lunar polar stereographic reprojection, and common ground sample "
            "distance normalisation across sensor pairs.",
      ),
      (
        "02",
        "RADIOMETRIC NORMALISATION",
        "Cross-modal histogram matching, DEM-based shadow masking using the "
            "cos \u03B2 illumination formula, and cosine terrain correction applied "
            "per pixel. Input quality gate rejects pairs with > 20% invalid pixels.",
      ),
      (
        "03",
        "RIFT2 PHASE CONGRUENCY EXTRACTION",
        "Radiation-variation insensitive feature transform. Log-Gabor filter "
            "bank across 4 scales \u00D7 6 orientations, multi-octave PC scale space, "
            "FAST keypoint detection, and 216-D maximum index map descriptors.",
      ),
      (
        "04",
        "HYPERNETWORK DESCRIPTOR MODULATION",
        "Per-channel adaptive scaling and shifting of the 216-D descriptor "
            "derived from global context. Deterministic weights seeded from 26166; "
            "interface ready for trained Hyp-Net weights.",
      ),
      (
        "05",
        "BFMAP + LOWE RATIO + MAGSAC++",
        "Brute-force L2 matching with 2-NN ratio rejection (d1 < 0.75 \u00B7 d2), "
            "then MAGSAC++ robust estimation via the OpenCV USAC backend with "
            "dynamic thresholding.",
      ),
      (
        "06",
        "SELF-CALIBRATING SCDF GATES",
        "Leave-one-out local-affine residual filter. Magnitude gate at "
            "med + 3\u03C3 (\u03C3 = 1.4826 \u00B7 MAD), LOO residual gate at med + 3.5\u03C3. "
            "Every threshold self-calibrates on the image pair. Zero hardcoded constants.",
      ),
      (
        "07",
        "SUB-PIXEL PARALLAX REFINEMENT",
        "Phase correlation on 64\u00D764 Hann-windowed patches with parabolic "
            "peak fitting. Delivers sub-pixel correspondence precision on lunar "
            "terrain features.",
      ),
      (
        "08",
        "THIN-PLATE SPLINE CORRECTION",
        "Bookstein 1989 non-rigid residual correction via scipy "
            "RBFInterpolator with thin_plate_spline kernel. 80/20 holdout "
            "residual validation ensures the improvement is measured on unseen inliers.",
      ),
      (
        "09",
        "FULL TELEMETRY PIPELINE",
        "HTML report generation with stage timeline, JSONL audit trail of "
            "every decision written to match_decisions.jsonl, and 18-assertion "
            "canary verification of all 17 required pipeline stages.",
      ),
    ];

    return _buildBlockList(stages, context, animTarget);
  }

  List<Widget> _buildBlockList(
      List<(String, String, String)> stages, BuildContext context, double? animTarget) {
    final widgets = <Widget>[];

    for (int i = 0; i < stages.length; i++) {
      final (num, title, desc) = stages[i];

      final stageBlock = Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: LunarTheme.surfaceCard,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: LunarTheme.border),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 32,
              height: 28,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: LunarTheme.surfaceElevated,
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: LunarTheme.borderLight),
              ),
              child: Text(
                num,
                style: LunarTheme.mono.copyWith(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.6,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    desc,
                    style: const TextStyle(
                        fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
                  ),
                ],
              ),
            ),
          ],
        ),
      );

      widgets.add(
        stageBlock
            .animate(target: animTarget, delay: (i * 100).ms)
            .fadeIn(duration: 300.ms, curve: Curves.easeOut)
            .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
      );

      if (i < stages.length - 1) {
        Widget arrow = const Padding(
          padding: EdgeInsets.symmetric(vertical: 4),
          child: Center(
            child: Icon(Icons.arrow_downward, size: 14, color: LunarTheme.textTertiary),
          ),
        );

        arrow = arrow.animate(
          target: animTarget,
          delay: (i * 100 + 50).ms,
          onPlay: (controller) {
            if (!AnimationUtils.isRunningInTest &&
                !AnimationUtils.isReducedMotion(context)) {
              controller.repeat(reverse: true);
            }
          },
        ).scale(
          begin: const Offset(0.9, 0.9),
          end: const Offset(1.15, 1.15),
          duration: 800.ms,
          curve: Curves.easeInOut,
        );

        widgets.add(arrow);
      }
    }

    return widgets;
  }
}
