import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../models/metrics_model.dart';
import '../models/image_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';
import '../widgets/spatial_grid_overlay.dart';

class SpatialCoverageScreen extends StatelessWidget {
  const SpatialCoverageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();
    final res = pipeProv.latestResponse;

    final spatialStats = res?.spatialStats ??
        const SpatialStatsModel(
          gridSize: 6,
          totalCells: 36,
          occupiedBefore: 14,
          occupiedAfter: 28,
          coveragePercentageBefore: 38.9,
          coveragePercentageAfter: 77.8,
          coverageGainPercentage: 38.9,
        );

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("SPATIAL COVERAGE ANALYSIS"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Grid Overlay Widget
              SpatialGridOverlayWidget(
                referenceImageWidget: _buildImageWidget(imgProv.referenceImage),
                spatialStats: spatialStats,
              ),
              const SizedBox(height: 16),

              // Scientific Motivation Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "WHY SPATIAL BALANCING MATTERS ON THE MOON",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      "Standard feature matching algorithms naturally concentrate hundreds of keypoints along the sharp, shadowed rims of a single prominent impact crater. "
                      "While this yields high inlier counts, it creates an ill-conditioned geometric fit that violently warps adjacent smooth mare plains.\n\n"
                      "LunarMatch enforces uniform spatial balancing by partitioning the lunar coordinate space into an N × N grid, ranking inliers within each cell, "
                      "and capping over-represented regions to maximize coverage across the entire image field.",
                      style: TextStyle(fontSize: 12, color: LunarTheme.textSecondary, height: 1.45),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Coverage Metric Formula Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "MEASURED COVERAGE FORMULATION",
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.8, color: LunarTheme.textTertiary),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Coverage = (Occupied Cells / Total Grid Cells) × 100%",
                      style: LunarTheme.mono.copyWith(fontSize: 11.5, color: Colors.white),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Before Balancing: ${spatialStats.occupiedBefore} / ${spatialStats.totalCells} cells (${spatialStats.coveragePercentageBefore}%)\n"
                      "After Balancing: ${spatialStats.occupiedAfter} / ${spatialStats.totalCells} cells (${spatialStats.coveragePercentageAfter}%)",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageWidget(LunarImageModel? img) {
    if (img == null) return const SizedBox();
    if (img.bytes != null) return Image.memory(img.bytes!, fit: BoxFit.cover);
    if (img.assetPath != null) return Image.asset(img.assetPath!, fit: BoxFit.cover);
    if (img.localPath != null) return Image.file(File(img.localPath!), fit: BoxFit.cover);
    return const SizedBox();
  }
}
