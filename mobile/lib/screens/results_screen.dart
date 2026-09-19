import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/image_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';
import '../widgets/metric_card.dart';
import '../widgets/image_comparison.dart';
import '../utils/formatters.dart';
import '../services/report_export_service.dart';
import '../utils/animation_utils.dart';

class ResultsScreen extends StatefulWidget {
  const ResultsScreen({super.key});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();
    final res = pipeProv.latestResponse;
    final animTarget = AnimationUtils.targetFor(context);

    if (res == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("REGISTRATION RESULT")),
        body: const Center(child: Text("No registration results.", style: TextStyle(color: LunarTheme.textSecondary))),
      );
    }

    final metrics = res.metrics;
    final isReliable = (res.status == "SUCCESSFUL" || res.status == "LOW_CONFIDENCE");

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            const Expanded(
              child: Text(
                "REGISTRATION RESULT",
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: Colors.white,
                ),
              ),
            ),

          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.download_outlined, size: 20, color: Colors.white),
            tooltip: "Export Insight Report",
            onPressed: () => ReportExportService.showExportModal(
              context: context,
              response: res,
              referenceSensor: imgProv.referenceSensor,
              movingSensor: imgProv.movingSensor,
            ),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Result Status Header Card: Responsive layout prevents title/badge collision
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: isReliable ? Colors.white : LunarTheme.borderFocus,
                    width: 1.2,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Icon(
                          isReliable ? Icons.verified_outlined : Icons.error_outline,
                          size: 18,
                          color: Colors.white,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            isReliable ? "REGISTRATION SUCCESSFUL" : "REGISTRATION NOT RELIABLE",
                            style: const TextStyle(
                              fontSize: 12.5,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.8,
                              color: Colors.white,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Quality Badge with Scale-in (300 ms)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: isReliable ? Colors.white : LunarTheme.borderFocus,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            isReliable ? "OPTIMAL" : "FAIL-SAFE",
                            style: TextStyle(
                              fontSize: 9.5,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.6,
                              color: isReliable ? Colors.black : Colors.white,
                            ),
                          ),
                        )
                            .animate(target: animTarget)
                            .scale(
                              begin: const Offset(0.8, 0.8),
                              end: const Offset(1.0, 1.0),
                              duration: 300.ms,
                              curve: Curves.easeOut,
                            ),
                      ],
                    ),

                    const SizedBox(height: 8),
                    Text(
                      metrics.confidenceExplanation,
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
                    ),
                    if (res.warnings.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        res.warnings.first,
                        style: const TextStyle(fontSize: 10, fontStyle: FontStyle.italic, color: LunarTheme.textTertiary),
                      ),
                    ],
                  ],
                ),
              )
                  .animate(target: animTarget)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Primary Visual Registration Viewer
              ImageComparisonViewer(
                referenceWidget: _buildImageWidget(imgProv.referenceImage),
                registeredUrl: res.registeredImageUrl,
                overlayUrl: res.overlayImageUrl,
                differenceUrl: res.differenceImageUrl,
              )
                  .animate(target: animTarget, delay: 100.ms)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Metrics Dashboard Title & Grid
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    "QUANTITATIVE METRICS",
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.0,
                      color: LunarTheme.textTertiary,
                    ),
                  ),
                  const SizedBox(height: 10),

                  // Metrics Grid (Responsive 2-column or 4-column)
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final isWide = constraints.maxWidth > 500;
                      final itemWidth = isWide ? (constraints.maxWidth - 24) / 4 : (constraints.maxWidth - 8) / 2;

                      return Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "KEYPOINTS",
                              value: "${metrics.keypointsReference} / ${metrics.keypointsMoving}",
                              subtitle: "Reference / Moving",
                              icon: Icons.grain,
                              countUpValue: metrics.keypointsReference.toDouble(),
                              countUpFormatter: (val) {
                                final ref = val.toInt();
                                final ratio = metrics.keypointsReference > 0
                                    ? metrics.keypointsMoving / metrics.keypointsReference
                                    : 1.0;
                                final mov = (val * ratio).toInt();
                                return "$ref / $mov";
                              },
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "CANDIDATE MATCHES",
                              value: "${metrics.candidateMatches}",
                              subtitle: "Raw 2-NN Pairs",
                              icon: Icons.alt_route,
                              countUpValue: metrics.candidateMatches.toDouble(),
                              countUpFormatter: (val) => "${val.toInt()}",
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "FILTERED MATCHES",
                              value: "${metrics.filteredMatches}",
                              subtitle: "Lowe's Ratio Pass",
                              icon: Icons.filter_alt_outlined,
                              countUpValue: metrics.filteredMatches.toDouble(),
                              countUpFormatter: (val) => "${val.toInt()}",
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "RANSAC INLIERS",
                              value: "${metrics.ransacInliers}",
                              subtitle: "Geometric Consensus",
                              icon: Icons.check_circle_outline,
                              countUpValue: metrics.ransacInliers.toDouble(),
                              countUpFormatter: (val) => "${val.toInt()}",
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "INLIER RATIO",
                              value: Formatters.formatPercentage(metrics.inlierRatio),
                              subtitle: "Inliers / Filtered",
                              icon: Icons.pie_chart_outline,
                              countUpValue: metrics.inlierRatio * 100.0,
                              countUpFormatter: (val) => "${val.toStringAsFixed(1)}%",
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "SPATIAL COVERAGE",
                              value: Formatters.formatPercentage(metrics.spatialCoverage),
                              subtitle: "Partition Grid Fill",
                              icon: Icons.grid_view,
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "REPROJECTION RMSE",
                              value: metrics.rmsePx != null ? Formatters.formatPixels(metrics.rmsePx) : "N/A",
                              subtitle: metrics.rmsePx != null ? "Residual Pixel Error" : "Unreliable / Skipped",
                              icon: Icons.straighten,
                              countUpValue: metrics.rmsePx,
                              countUpFormatter: (val) => "${val.toStringAsFixed(2)} px",
                            ),
                          ),
                          SizedBox(
                            width: itemWidth,
                            child: MetricCard(
                              title: "RUNTIME",
                              value: Formatters.formatMilliseconds(metrics.runtimeMs),
                              subtitle: "End-to-End Latency",
                              icon: Icons.timer_outlined,
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 200.ms)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Action Buttons Section
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Export Insight Report Action Button
                  ElevatedButton.icon(
                    onPressed: () => ReportExportService.showExportModal(
                      context: context,
                      response: res,
                      referenceSensor: imgProv.referenceSensor,
                      movingSensor: imgProv.movingSensor,
                    ),
                    icon: const Icon(Icons.assessment_outlined, size: 18),
                    label: const Text(
                      "EXPORT INSIGHT REPORT",
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.8),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                  const SizedBox(height: 10),

                  // Action Navigation Buttons
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final isVeryNarrow = constraints.maxWidth < 320;

                      final corrBtn = OutlinedButton.icon(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.correspondence),
                        icon: const Icon(Icons.hub_outlined, size: 16),
                        label: const Text("VIEW CORRESPONDENCES"),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
                          foregroundColor: Colors.white,
                          side: const BorderSide(color: LunarTheme.borderLight),
                        ),
                      );

                      final gridBtn = OutlinedButton.icon(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.spatialCoverage),
                        icon: const Icon(Icons.grid_4x4, size: 16),
                        label: const Text("SPATIAL GRID"),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
                          foregroundColor: Colors.white,
                          side: const BorderSide(color: LunarTheme.borderLight),
                        ),
                      );

                      if (isVeryNarrow) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            corrBtn,
                            const SizedBox(height: 8),
                            gridBtn,
                          ],
                        );
                      }

                      return Row(
                        children: [
                          Expanded(child: corrBtn),
                          const SizedBox(width: 8),
                          Expanded(child: gridBtn),
                        ],
                      );
                    },
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 300.ms)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 12),

              if (res.subpixelDiagnostics != null && res.subpixelDiagnostics!.enabled) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "SUB-PIXEL REFINEMENT",
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 1.0, color: LunarTheme.textTertiary),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text("Median Residual", style: TextStyle(fontSize: 9.5, color: LunarTheme.textSecondary)),
                                Text(
                                  res.subpixelDiagnostics!.medianResidualPx != null ? "${res.subpixelDiagnostics!.medianResidualPx!.toStringAsFixed(3)} px" : "N/A",
                                  style: LunarTheme.mono.copyWith(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text("P95 Residual", style: TextStyle(fontSize: 9.5, color: LunarTheme.textSecondary)),
                                Text(
                                  res.subpixelDiagnostics!.p95ResidualPx != null ? "${res.subpixelDiagnostics!.p95ResidualPx!.toStringAsFixed(3)} px" : "N/A",
                                  style: LunarTheme.mono.copyWith(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text("Refined Points", style: TextStyle(fontSize: 9.5, color: LunarTheme.textSecondary)),
                                Text(
                                  "${res.subpixelDiagnostics!.nRefined}",
                                  style: LunarTheme.mono.copyWith(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
              ],
              if (res.routingConfig != null && res.routingConfig!.rationale.isNotEmpty) ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  child: Text(
                    res.routingConfig!.rationale,
                    style: const TextStyle(fontSize: 10, color: LunarTheme.textSecondary),
                  ),
                ),
                const SizedBox(height: 12),
              ],
              // Expandable Transformation Matrix Section
              Container(
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    title: const Text(
                      "GEOMETRIC TRANSFORMATION MATRIX",
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.6, color: Colors.white),
                    ),
                    subtitle: Text(
                      res.transformationMatrix != null ? "Computed 3x3 Projective Matrix" : "Matrix not computed",
                      style: const TextStyle(fontSize: 10, color: LunarTheme.textTertiary),
                    ),
                    iconColor: Colors.white,
                    collapsedIconColor: LunarTheme.textTertiary,
                    children: [
                      if (res.transformationMatrix != null)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          child: Column(
                            children: res.transformationMatrix!.map((row) {
                              return Padding(
                                padding: const EdgeInsets.symmetric(vertical: 3),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                  children: row.map((val) {
                                    return Expanded(
                                      child: Text(
                                        val.toStringAsFixed(5),
                                        textAlign: TextAlign.center,
                                        style: LunarTheme.mono.copyWith(fontSize: 11),
                                      ),
                                    );
                                  }).toList(),
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Pipeline Details navigation
              OutlinedButton.icon(
                onPressed: () => Navigator.pushNamed(context, AppRoutes.pipelineDetails),
                icon: const Icon(Icons.timeline_outlined, size: 16),
                label: const Text("VIEW PIPELINE DETAILS"),
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
    if (img.bytes != null) return Image.memory(img.bytes!, fit: BoxFit.contain);
    if (img.assetPath != null) return Image.asset(img.assetPath!, fit: BoxFit.contain);
    if (img.localPath != null) return Image.file(File(img.localPath!), fit: BoxFit.contain);
    return const SizedBox();
  }
}
