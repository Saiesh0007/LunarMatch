import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/image_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({super.key});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();
    final res = pipeProv.latestResponse;

    if (res == null) {
      return Scaffold(
        backgroundColor: LunarTheme.background,
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
            onPressed: () => Navigator.pop(context),
          ),
          title: const Text("Results"),
        ),
        body: const Center(
          child: Text("No registration results available.", style: TextStyle(color: LunarTheme.textSecondary)),
        ),
      );
    }

    final metrics = res.metrics;
    final isReliable = (res.status == "SUCCESSFUL" || res.status == "LOW_CONFIDENCE");

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false),
        ),
        title: const Text("Results"),
        centerTitle: false,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: LunarTheme.primary,
          labelColor: LunarTheme.primary,
          unselectedLabelColor: LunarTheme.textTertiary,
          labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, letterSpacing: 0.5),
          tabs: const [
            Tab(text: "Overlay"),
            Tab(text: "Match Points"),
            Tab(text: "Heatmap"),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Split image viewer with tabs
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildOverlayView(imgProv.referenceImage, res.registeredImageUrl),
                  _buildMatchPointsView(),
                  _buildHeatmapView(),
                ],
              ),
            ),

            // Metric cards grid (2x3)
            Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(child: _buildMetricCard("RMSE", metrics.rmsePx?.toStringAsFixed(2) ?? "N/A", "px")),
                      const SizedBox(width: 12),
                      Expanded(child: _buildMetricCard("Inliers", metrics.ransacInliers.toString(), "")),
                      const SizedBox(width: 12),
                      Expanded(child: _buildMetricCard("Inlier Ratio", (metrics.inlierRatio * 100).toStringAsFixed(1), "%")),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _buildMetricCard("Coverage", (metrics.spatialCoverage * 100).toStringAsFixed(1), "%")),
                      const SizedBox(width: 12),
                      Expanded(child: _buildMetricCard("Runtime", "${metrics.runtimeMs} ms", "")),
                      const SizedBox(width: 12),
                      Expanded(child: _buildMetricCard("Decision", isReliable ? "RELIABLE" : "UNRELIABLE", "")),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Action buttons
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            // Export results
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: LunarTheme.primary,
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                          child: const Text("Export Results"),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            // View full resolution
                          },
                          style: OutlinedButton.styleFrom(
                            foregroundColor: LunarTheme.primary,
                            side: BorderSide(color: LunarTheme.primary, width: 1),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                          ),
                          child: const Text("View Full Resolution"),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverlayView(LunarImageModel? refImage, String? registeredUrl) {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        children: [
          Expanded(
            child: Center(
              child: refImage != null
                  ? _buildImageWidget(refImage)
                  : const Text("No image", style: TextStyle(color: LunarTheme.textTertiary)),
            ),
          ),
          Container(
            height: 2,
            color: LunarTheme.primary,
          ),
          Expanded(
            child: Center(
              child: registeredUrl != null
                  ? Image.network(registeredUrl, fit: BoxFit.contain)
                  : const Text("Registered image", style: TextStyle(color: LunarTheme.textTertiary)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMatchPointsView() {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: const Center(
        child: Text("Match points visualization", style: TextStyle(color: LunarTheme.textTertiary)),
      ),
    );
  }

  Widget _buildHeatmapView() {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: const Center(
        child: Text("Error heatmap visualization", style: TextStyle(color: LunarTheme.textTertiary)),
      ),
    );
  }

  Widget _buildMetricCard(String title, String value, String unit) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.2,
              color: LunarTheme.textTertiary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: LunarTheme.mono.copyWith(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: LunarTheme.textPrimary,
            ),
          ),
          if (unit.isNotEmpty)
            Text(
              unit,
              style: LunarTheme.mono.copyWith(fontSize: 10, color: LunarTheme.textTertiary),
            ),
        ],
      ),
    );
  }

  Widget _buildImageWidget(LunarImageModel? img) {
    if (img == null) return const SizedBox();
    if (img.bytes != null) return Image.memory(img.bytes!, fit: BoxFit.contain);
    if (img.assetPath != null) return Image.asset(img.assetPath!, fit: BoxFit.contain);
    if (img.localPath != null) return Image.file(File(img.localPath!), fit: BoxFit.contain);
    return const SizedBox();
  }
}