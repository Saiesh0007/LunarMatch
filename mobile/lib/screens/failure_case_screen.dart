import 'package:flutter/material.dart';
import '../app/theme.dart';

class FailureCaseScreen extends StatelessWidget {
  const FailureCaseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Failure Case"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Alert panel
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.error.withOpacity(0.5), width: 1),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: LunarTheme.error.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.warning, color: LunarTheme.error, size: 18),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Registration Not Reliable",
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w800,
                              color: LunarTheme.error,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Image pair placeholder
              Container(
                height: 160,
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.image_not_supported, size: 40, color: LunarTheme.textTertiary),
                      const SizedBox(height: 8),
                      Text(
                        "Rejected pair visualization\nOutliers shown in red",
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 11, color: LunarTheme.textTertiary, height: 1.5),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 7-row checklist
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "ACCEPTANCE CRITERIA",
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: LunarTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ..._buildChecklistItems(),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Reason card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.error.withOpacity(0.5), width: 1),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "REGISTRATION_NOT_RELIABLE",
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.8,
                        color: LunarTheme.error,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "REGISTRATION_NOT_RELIABLE — 3 criteria failed: Inlier Ratio, Spatial Coverage, RMSE",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textPrimary),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Why this matters
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "WHY THIS MATTERS",
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: LunarTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "We return NOT_RELIABLE rather than a wrong transform. Downstream users can trust the metric. A false positive registration would propagate coordinate errors into lunar mapping products.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.5),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildChecklistItems() {
    final items = [
      {"label": "Inlier Ratio ≥ 0.4", "value": "0.23", "pass": false, "threshold": "≥ 0.40"},
      {"label": "RANSAC Inliers ≥ 30", "value": "18", "pass": false, "threshold": "≥ 30"},
      {"label": "Spatial Coverage ≥ 40%", "value": "31.2%", "pass": false, "threshold": "≥ 40%"},
      {"label": "RMSE ≤ 3.0 px", "value": "5.67 px", "pass": false, "threshold": "≤ 3.0 px"},
      {"label": "Keypoints Detected ≥ 100", "value": "247", "pass": true, "threshold": "≥ 100"},
      {"label": "Candidate Matches ≥ 50", "value": "89", "pass": true, "threshold": "≥ 50"},
      {"label": "Geometric Model Valid", "value": "Yes", "pass": true, "threshold": "Valid"},
    ];

    return items.map((item) {
      final pass = item["pass"] as bool;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(
          children: [
            Icon(
              pass ? Icons.check_circle : Icons.cancel,
              size: 18,
              color: pass ? LunarTheme.success : LunarTheme.error,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                item["label"] as String,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: pass ? LunarTheme.textPrimary : LunarTheme.textSecondary,
                ),
              ),
            ),
            Text(
              item["value"] as String,
              style: LunarTheme.mono.copyWith(fontSize: 11, color: LunarTheme.textPrimary),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: pass ? LunarTheme.success : LunarTheme.error,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                pass ? "PASS" : "FAIL",
                style: const TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w900,
                  color: Colors.black,
                ),
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 60,
              child: Text(
                item["threshold"] as String,
                style: const TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
                textAlign: TextAlign.right,
              ),
            ),
          ],
        ),
      );
    }).toList();
  }
}