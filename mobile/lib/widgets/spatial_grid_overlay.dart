import 'package:flutter/material.dart';
import '../models/metrics_model.dart';
import '../app/theme.dart';

class SpatialGridOverlayWidget extends StatefulWidget {
  final Widget referenceImageWidget;
  final SpatialStatsModel spatialStats;

  const SpatialGridOverlayWidget({
    super.key,
    required this.referenceImageWidget,
    required this.spatialStats,
  });

  @override
  State<SpatialGridOverlayWidget> createState() => _SpatialGridOverlayWidgetState();
}

class _SpatialGridOverlayWidgetState extends State<SpatialGridOverlayWidget> {
  bool _showAfterBalancing = true;

  @override
  Widget build(BuildContext context) {
    final stats = widget.spatialStats;
    final gridSize = stats.gridSize;
    final totalCells = stats.totalCells;

    final occupied = _showAfterBalancing ? stats.occupiedAfter : stats.occupiedBefore;

    return Container(
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Responsive Header & Toggle
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "SPATIAL COVERAGE GRID",
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      "$gridSize × $gridSize uniform partitioning",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textTertiary),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // Toggle
              Container(
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildToggleButton("BEFORE", !_showAfterBalancing, () {
                      setState(() => _showAfterBalancing = false);
                    }),
                    _buildToggleButton("AFTER", _showAfterBalancing, () {
                      setState(() => _showAfterBalancing = true);
                    }),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Visual Grid Canvas over Reference Image
          Container(
            height: 260,
            decoration: BoxDecoration(
              color: LunarTheme.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: LunarTheme.border),
            ),
            clipBehavior: Clip.antiAlias,
            child: Stack(
              fit: StackFit.expand,
              children: [
                widget.referenceImageWidget,

                // Grid Painter
                CustomPaint(
                  painter: GridCellPainter(
                    gridSize: gridSize,
                    occupiedCellsCount: occupied,
                    totalCells: totalCells,
                    highlightColor: Colors.white,
                  ),
                ),

                // Floating telemetry badge
                Positioned(
                  bottom: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.8),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: LunarTheme.borderLight),
                    ),
                    child: Text(
                      "$occupied / $totalCells CELLS OCCUPIED",
                      style: LunarTheme.mono.copyWith(fontSize: 10.5, color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Quantitative Summary Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            decoration: BoxDecoration(
              color: LunarTheme.surfaceElevated,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: LunarTheme.border),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Expanded(child: _buildStatItem("Before", "${stats.coveragePercentageBefore}%", LunarTheme.textSecondary)),
                Container(width: 1, height: 24, color: LunarTheme.border),
                Expanded(child: _buildStatItem("After", "${stats.coveragePercentageAfter}%", Colors.white)),
                Container(width: 1, height: 24, color: LunarTheme.border),
                Expanded(
                  child: _buildStatItem(
                    "Gain",
                    stats.coverageGainPercentage >= 0 ? "+${stats.coverageGainPercentage}%" : "${stats.coverageGainPercentage}%",
                    Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildToggleButton(String label, bool isSelected, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            color: isSelected ? Colors.black : LunarTheme.textTertiary,
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color valColor) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            fontFamily: 'Courier',
            fontFamilyFallback: const ['monospace'],
            fontSize: 13,
            fontWeight: FontWeight.w800,
            color: valColor,
          ),
        ),
      ],
    );
  }
}

class GridCellPainter extends CustomPainter {
  final int gridSize;
  final int occupiedCellsCount;
  final int totalCells;
  final Color highlightColor;

  GridCellPainter({
    required this.gridSize,
    required this.occupiedCellsCount,
    required this.totalCells,
    required this.highlightColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cellW = size.width / gridSize;
    final cellH = size.height / gridSize;

    final gridLinePaint = Paint()
      ..color = Colors.white.withOpacity(0.18)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    final occupiedPaint = Paint()
      ..color = highlightColor.withOpacity(0.20)
      ..style = PaintingStyle.fill;

    final occupiedBorderPaint = Paint()
      ..color = highlightColor.withOpacity(0.65)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    int drawnOccupied = 0;

    for (int r = 0; r < gridSize; r++) {
      for (int c = 0; c < gridSize; c++) {
        final rect = Rect.fromLTWH(c * cellW, r * cellH, cellW, cellH);
        final isOccupiedCell = ((r * 3 + c * 5 + 1) % totalCells) < occupiedCellsCount;

        if (isOccupiedCell && drawnOccupied < occupiedCellsCount) {
          canvas.drawRect(rect, occupiedPaint);
          canvas.drawRect(rect, occupiedBorderPaint);
          drawnOccupied++;
        }

        canvas.drawRect(rect, gridLinePaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant GridCellPainter oldDelegate) {
    return oldDelegate.occupiedCellsCount != occupiedCellsCount ||
        oldDelegate.gridSize != gridSize ||
        oldDelegate.highlightColor != highlightColor;
  }
}
