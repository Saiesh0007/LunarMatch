import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../app/theme.dart';

class RobustnessScreen extends StatefulWidget {
  const RobustnessScreen({super.key});

  @override
  State<RobustnessScreen> createState() => _RobustnessScreenState();
}

class _RobustnessScreenState extends State<RobustnessScreen> {
  int _selectedTab = 0;
  final List<String> _tabs = ["Illumination", "Scale", "Rotation", "Translation"];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Robustness Lab"),
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
                      "PROTOTYPE SENSITIVITY SWEEP",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: LunarTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Evaluates correspondence degradation across controlled synthetic variations in illumination angle, optical scale, in-plane rotation, and camera translation.",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 4-tab segmented control
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SegmentedButton<int>(
                  segments: [
                    ButtonSegment(value: 0, label: Text(_tabs[0], style: const TextStyle(fontSize: 11))),
                    ButtonSegment(value: 1, label: Text(_tabs[1], style: const TextStyle(fontSize: 11))),
                    ButtonSegment(value: 2, label: Text(_tabs[2], style: const TextStyle(fontSize: 11))),
                    ButtonSegment(value: 3, label: Text(_tabs[3], style: const TextStyle(fontSize: 11))),
                  ],
                  selected: {_selectedTab},
                  onSelectionChanged: (Set<int> newSelection) {
                    setState(() {
                      _selectedTab = newSelection.first;
                    });
                  },
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.resolveWith<Color>((states) {
                      if (states.contains(WidgetState.selected)) {
                        return LunarTheme.primary;
                      }
                      return LunarTheme.surfaceCard;
                    }),
                    foregroundColor: WidgetStateProperty.resolveWith<Color>((states) {
                      if (states.contains(WidgetState.selected)) {
                        return Colors.black;
                      }
                      return LunarTheme.textPrimary;
                    }),
                    side: WidgetStateProperty.all(BorderSide(color: LunarTheme.border, width: 1)),
                    shape: WidgetStateProperty.all(
                      RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Run experiment button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // Run experiment
                  },
                  icon: const Icon(Icons.play_arrow_rounded, size: 20),
                  label: const Text(
                    "RUN EXPERIMENT SWEEP",
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: LunarTheme.primary,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Line chart with two lines
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
                    Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 12,
                      runSpacing: 8,
                      children: [
                        Text(
                          "INLIER RATIO (%) VS VARIATION",
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                            color: LunarTheme.textPrimary,
                          ),
                        ),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _buildLegendDot(LunarTheme.primary, "LunarMatch"),
                            const SizedBox(width: 12),
                            _buildLegendDot(LunarTheme.textSecondary, "SIFT Baseline"),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 240,
                      child: LineChart(
                        _buildDualLineChartData(),
                      ),
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

  Widget _buildLegendDot(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(fontSize: 10, color: LunarTheme.textSecondary),
        ),
      ],
    );
  }

  LineChartData _buildDualLineChartData() {
    // Mock data: LunarMatch (flat saffron line) vs SIFT (dropping grey line)
    final lunarSpots = [
      const FlSpot(0, 92),
      const FlSpot(1, 90),
      const FlSpot(2, 88),
      const FlSpot(3, 86),
      const FlSpot(4, 84),
      const FlSpot(5, 82),
      const FlSpot(6, 80),
    ];

    final siftSpots = [
      const FlSpot(0, 92),
      const FlSpot(1, 78),
      const FlSpot(2, 65),
      const FlSpot(3, 52),
      const FlSpot(4, 40),
      const FlSpot(5, 28),
      const FlSpot(6, 18),
    ];

    return LineChartData(
      gridData: FlGridData(
        show: true,
        drawVerticalLine: false,
        getDrawingHorizontalLine: (val) => FlLine(
          color: LunarTheme.surfaceElevated,
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
              if (idx >= 0 && idx < 7) {
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
                "${val.toInt()}%",
                style: const TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
              );
            },
          ),
        ),
      ),
      borderData: FlBorderData(
        show: true,
        border: Border(
          bottom: BorderSide(color: LunarTheme.border, width: 1),
          left: BorderSide(color: LunarTheme.border, width: 1),
        ),
      ),
      lineBarsData: [
        LineChartBarData(
          spots: lunarSpots,
          isCurved: true,
          curveSmoothness: 0.35,
          color: LunarTheme.primary,
          barWidth: 2.5,
          isStrokeCapRound: true,
          dotData: FlDotData(
            show: true,
            getDotPainter: (spot, percent, barData, index) {
              return FlDotCirclePainter(
                radius: 4,
                color: Colors.black,
                strokeWidth: 2,
                strokeColor: LunarTheme.primary,
              );
            },
          ),
          belowBarData: BarAreaData(
            show: true,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                LunarTheme.primary.withOpacity(0.18),
                LunarTheme.primary.withOpacity(0.0),
              ],
            ),
          ),
        ),
        LineChartBarData(
          spots: siftSpots,
          isCurved: true,
          curveSmoothness: 0.35,
          color: LunarTheme.textSecondary,
          barWidth: 2,
          isStrokeCapRound: true,
          dotData: FlDotData(
            show: true,
            getDotPainter: (spot, percent, barData, index) {
              return FlDotCirclePainter(
                radius: 3,
                color: Colors.black,
                strokeWidth: 2,
                strokeColor: LunarTheme.textSecondary,
              );
            },
          ),
          belowBarData: BarAreaData(
            show: false,
          ),
        ),
      ],
      minX: 0,
      maxX: 6,
      minY: 0,
      maxY: 100,
    );
  }
}