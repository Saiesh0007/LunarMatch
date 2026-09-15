import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../app/theme.dart';
import '../models/experiment_model.dart';
import '../providers/experiment_provider.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';
import '../utils/formatters.dart';

class RobustnessScreen extends StatelessWidget {
  const RobustnessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final expProv = context.watch<ExperimentProvider>();
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();

    final exp = expProv.latestExperiment;
    final isOffline = !pipeProv.isBackendConnected;
    final baseId = imgProv.referenceImage?.id ?? "demo_pair_a_ref";

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("ROBUSTNESS LABORATORY"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Technical Header Banner
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
                      "SENSITIVITY SWEEP",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      "Evaluates correspondence degradation across controlled synthetic variations in illumination angle, optical scale, in-plane rotation, and camera translation.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Experiment Parameter Controls Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "EXPERIMENT CONFIGURATION",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Variation Type Selector: Wrap prevents overflow on narrow screens
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildTypeChip("illumination", "ILLUMINATION", Icons.wb_sunny_outlined, expProv),
                        _buildTypeChip("scale", "SCALE", Icons.aspect_ratio_outlined, expProv),
                        _buildTypeChip("rotation", "ROTATION", Icons.rotate_right_outlined, expProv),
                        _buildTypeChip("translation", "TRANSLATION", Icons.open_with_outlined, expProv),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Steps Selector
                    Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 8,
                      runSpacing: 6,
                      children: [
                        const Text(
                          "Variation Steps:",
                          style: TextStyle(fontSize: 12, color: LunarTheme.textSecondary),
                        ),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [3, 5, 7].map((s) {
                            final isSel = expProv.variationSteps == s;
                            return Padding(
                              padding: const EdgeInsets.only(left: 6),
                              child: InkWell(
                                onTap: () => expProv.setSteps(s),
                                borderRadius: BorderRadius.circular(4),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: isSel ? Colors.white : LunarTheme.surfaceElevated,
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(
                                      color: isSel ? Colors.white : LunarTheme.border,
                                    ),
                                  ),
                                  child: Text(
                                    "$s",
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w800,
                                      color: isSel ? Colors.black : Colors.white,
                                    ),
                                  ),
                                ),
                              ),
                            );
                          }).toList(),
                        ),
                      ],
                    ),
                    const SizedBox(height: 18),

                    // Run Button: Sized to full available width
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: expProv.isLoading
                            ? null
                            : () {
                                expProv.runExperiment(
                                  baseImageId: baseId,
                                  config: pipeProv.config,
                                  isOffline: isOffline,
                                );
                              },
                        icon: expProv.isLoading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                              )
                            : const Icon(Icons.play_arrow_rounded, size: 20),
                        label: Text(
                          expProv.isLoading ? "RUNNING EXPERIMENT SWEEP..." : "RUN EXPERIMENT SWEEP",
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                          ),
                        ),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          backgroundColor: Colors.white,
                          foregroundColor: Colors.black,
                          disabledBackgroundColor: const Color(0xFF222222),
                          disabledForegroundColor: const Color(0xFF555555),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Charts and Results Section
              if (exp != null && exp.points.isNotEmpty) ...[
                // Metric Chart: Inlier Ratio vs Variation
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        alignment: WrapAlignment.spaceBetween,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          const Text(
                            "INLIER RATIO (%) VS VARIATION",
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.8,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            "Peak: ${exp.summary['peak_inliers']} inliers",
                            style: LunarTheme.mono.copyWith(fontSize: 10, color: Colors.white),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 180,
                        child: LineChart(
                          _buildLineChartData(
                            exp.points,
                            (p) => p.inlierRatio,
                            Colors.white,
                            "%",
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Metric Chart: Spatial Coverage vs Variation
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        alignment: WrapAlignment.spaceBetween,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        spacing: 8,
                        runSpacing: 4,
                        children: const [
                          Text(
                            "SPATIAL COVERAGE (%) VS VARIATION",
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.8,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 180,
                        child: LineChart(
                          _buildLineChartData(
                            exp.points,
                            (p) => p.spatialCoverage,
                            const Color(0xFFB0B0B0),
                            "%",
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Table of Points
                Container(
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "MEASURED DATA POINTS",
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.8,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 10),
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: DataTable(
                          columnSpacing: 16,
                          headingRowHeight: 32,
                          dataRowMinHeight: 36,
                          dataRowMaxHeight: 36,
                          columns: const [
                            DataColumn(label: Text("STEP", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                            DataColumn(label: Text("INLIERS", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                            DataColumn(label: Text("RATIO", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                            DataColumn(label: Text("COVERAGE", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                            DataColumn(label: Text("RMSE", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                            DataColumn(label: Text("STATUS", style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white))),
                          ],
                          rows: exp.points.map((p) {
                            final isPass = p.status == "SUCCESSFUL";
                            return DataRow(
                              cells: [
                                DataCell(Text(p.variationLabel, style: LunarTheme.mono.copyWith(fontSize: 11))),
                                DataCell(Text("${p.inliers}", style: LunarTheme.mono.copyWith(fontSize: 11))),
                                DataCell(Text(Formatters.formatPercentage(p.inlierRatio), style: LunarTheme.mono.copyWith(fontSize: 11))),
                                DataCell(Text(Formatters.formatPercentage(p.spatialCoverage), style: LunarTheme.mono.copyWith(fontSize: 11))),
                                DataCell(Text(
                                  p.rmsePx != null ? "${p.rmsePx!.toStringAsFixed(2)} px" : "N/A",
                                  style: LunarTheme.mono.copyWith(fontSize: 11),
                                )),
                                DataCell(
                                  Text(
                                    isPass ? "PASS" : "DEGRADED",
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                      color: isPass ? Colors.white : LunarTheme.textTertiary,
                                    ),
                                  ),
                                ),
                              ],
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTypeChip(String typeKey, String label, IconData icon, ExperimentProvider prov) {
    final isSelected = prov.experimentType == typeKey;

    return InkWell(
      onTap: () => prov.setExperimentType(typeKey),
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : LunarTheme.surfaceElevated,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isSelected ? Colors.white : LunarTheme.border,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 14,
              color: isSelected ? Colors.black : LunarTheme.textSecondary,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
                color: isSelected ? Colors.black : LunarTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  LineChartData _buildLineChartData(
    List<RobustnessPointModel> points,
    double Function(RobustnessPointModel) valueGetter,
    Color color,
    String unit,
  ) {
    final spots = <FlSpot>[];
    for (int i = 0; i < points.length; i++) {
      spots.add(FlSpot(i.toDouble(), valueGetter(points[i])));
    }

    return LineChartData(
      gridData: FlGridData(
        show: true,
        drawVerticalLine: false,
        getDrawingHorizontalLine: (val) => FlLine(
          color: const Color(0xFF222222),
          strokeWidth: 1,
        ),
      ),
      titlesData: FlTitlesData(
        topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            getTitlesWidget: (val, meta) {
              final idx = val.toInt();
              if (idx >= 0 && idx < points.length) {
                return Text(
                  "S$idx",
                  style: const TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
                );
              }
              return const SizedBox();
            },
          ),
        ),
        leftTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 34,
            getTitlesWidget: (val, meta) {
              return Text(
                "${val.toInt()}$unit",
                style: const TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
              );
            },
          ),
        ),
      ),
      borderData: FlBorderData(
        show: true,
        border: const Border(
          bottom: BorderSide(color: LunarTheme.border, width: 1),
          left: BorderSide(color: LunarTheme.border, width: 1),
        ),
      ),
      lineBarsData: [
        LineChartBarData(
          spots: spots,
          isCurved: true,
          curveSmoothness: 0.35,
          color: color,
          barWidth: 2,
          isStrokeCapRound: true,
          dotData: FlDotData(
            show: true,
            getDotPainter: (spot, percent, barData, index) {
              return FlDotCirclePainter(
                radius: 3,
                color: Colors.black,
                strokeWidth: 2,
                strokeColor: color,
              );
            },
          ),
          belowBarData: BarAreaData(
            show: true,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                color.withOpacity(0.18),
                color.withOpacity(0.0),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
