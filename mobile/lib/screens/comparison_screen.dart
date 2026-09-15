import 'package:flutter/material.dart';
import '../app/theme.dart';

class ComparisonScreen extends StatelessWidget {
  const ComparisonScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Comparison"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
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
                      "SIFT vs LunarMatch — Same Input Pair",
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.6,
                        color: LunarTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "Pair A",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Two-column comparison
              LayoutBuilder(
                builder: (context, constraints) {
                  final isWide = constraints.maxWidth > 700;
                  if (isWide) {
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: _buildPipelineCard("SIFT BASELINE", _siftData(), false)),
                        const SizedBox(width: 12),
                        Expanded(child: _buildPipelineCard("LUNARMATCH (RIFT2)", _lunarData(), true)),
                      ],
                    );
                  }
                  return Column(
                    children: [
                      _buildPipelineCard("SIFT BASELINE", _siftData(), false),
                      const SizedBox(height: 12),
                      _buildPipelineCard("LUNARMATCH (RIFT2)", _lunarData(), true),
                    ],
                  );
                },
              ),

            ],
          ),
        ),
      ),
    );
  }

  Map<String, dynamic> _siftData() {
    return {
      'status': 'ACCEPTED',
      'inliers': 847,
      'rmse_px': 2.34,
      'coverage': 0.62,
      'inlier_ratio': 0.58,
    };
  }

  Map<String, dynamic> _lunarData() {
    return {
      'status': 'ACCEPTED',
      'inliers': 1243,
      'rmse_px': 1.18,
      'coverage': 0.87,
      'inlier_ratio': 0.79,
    };
  }

  Widget _buildPipelineCard(String title, Map<String, dynamic> data, bool isLunarMatch) {
    final status = data['status'] ?? 'UNKNOWN';
    final isFailed = status == 'FAILED' || status == 'NOT_RELIABLE' || status == 'REGISTRATION_NOT_RELIABLE';
    final isAccepted = status == 'ACCEPTED' || status == 'SUCCESSFUL';
    final inliers = data['inliers'] ?? 0;
    final rmsePx = data['rmse_px'];
    final coverage = data['coverage'] ?? 0.0;
    final inlierRatio = data['inlier_ratio'] ?? 0.0;

    final accentColor = isLunarMatch ? LunarTheme.primary : LunarTheme.success;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isFailed ? LunarTheme.border : accentColor,
          width: isFailed ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 0.6,
                    color: isFailed ? LunarTheme.border : accentColor,
                  ),
                ),
              ),
              if (isFailed)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: LunarTheme.border,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    status == 'NOT_RELIABLE' || status == 'REGISTRATION_NOT_RELIABLE' ? "REJECTED" : "FAILED",
                    style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.black),
                  ),
                )
              else if (isAccepted)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: accentColor,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text("ACCEPTED", style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.black)),
                ),
            ],
          ),
          const SizedBox(height: 16),
          _metricRow("INLIERS", "$inliers", "Geometric consensus", "RMSE", rmsePx != null ? "${rmsePx.toStringAsFixed(2)} px" : "N/A", "Reprojection error"),
          const SizedBox(height: 12),
          _metricRow("COVERAGE", "${(coverage * 100).toStringAsFixed(1)}%", "Grid occupancy", "INLIER RATIO", "${(inlierRatio * 100).toStringAsFixed(1)}%", "Filtered matches"),
        ],
      ),
    );
  }

  Widget _metricRow(
    String labelA, String valueA, String subtitleA,
    String labelB, String valueB, String subtitleB,
  ) {
    return Row(
      children: [
        Expanded(child: _buildMetricItem(labelA, valueA, subtitleA)),
        const SizedBox(width: 8),
        Expanded(child: _buildMetricItem(labelB, valueB, subtitleB)),
      ],
    );
  }

  Widget _buildMetricItem(String label, String value, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.2,
            color: LunarTheme.textTertiary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: LunarTheme.mono.copyWith(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: LunarTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          subtitle,
          style: const TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
        ),
      ],
    );
  }
}