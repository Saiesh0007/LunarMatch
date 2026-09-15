import 'package:flutter/material.dart';
import '../models/match_model.dart';
import '../app/theme.dart';

enum MatchFilterTab { candidates, filtered, inliers, spatial }

class MatchVisualizationWidget extends StatefulWidget {
  final List<MatchPairModel> matches;
  final Widget refImageWidget;
  final Widget movImageWidget;
  final int refWidth;
  final int refHeight;

  const MatchVisualizationWidget({
    super.key,
    required this.matches,
    required this.refImageWidget,
    required this.movImageWidget,
    this.refWidth = 640,
    this.refHeight = 640,
  });

  @override
  State<MatchVisualizationWidget> createState() => _MatchVisualizationWidgetState();
}

class _MatchVisualizationWidgetState extends State<MatchVisualizationWidget> {
  MatchFilterTab _activeTab = MatchFilterTab.inliers;

  @override
  Widget build(BuildContext context) {
    List<MatchPairModel> displayMatches;
    switch (_activeTab) {
      case MatchFilterTab.candidates:
        displayMatches = widget.matches;
        break;
      case MatchFilterTab.filtered:
        displayMatches = widget.matches;
        break;
      case MatchFilterTab.inliers:
        displayMatches = widget.matches.where((m) => m.isInlier).toList();
        break;
      case MatchFilterTab.spatial:
        displayMatches = widget.matches.where((m) => m.isSpatiallySelected).toList();
        if (displayMatches.isEmpty) {
          displayMatches = widget.matches.where((m) => m.isInlier).take(48).toList();
        }
        break;
    }

    final candidateCount = widget.matches.length;
    final inlierCount = widget.matches.where((m) => m.isInlier).length;
    final spatialCount = widget.matches.where((m) => m.isSpatiallySelected).length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Tabs Container
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          decoration: BoxDecoration(
            color: LunarTheme.surfaceCard,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
            border: Border.all(color: LunarTheme.border),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildTab(MatchFilterTab.candidates, "CANDIDATES ($candidateCount)"),
                const SizedBox(width: 4),
                _buildTab(MatchFilterTab.filtered, "FILTERED ($candidateCount)"),
                const SizedBox(width: 4),
                _buildTab(MatchFilterTab.inliers, "RANSAC INLIERS ($inlierCount)"),
                const SizedBox(width: 4),
                _buildTab(MatchFilterTab.spatial, "BALANCED (${spatialCount > 0 ? spatialCount : inlierCount})"),
              ],
            ),
          ),
        ),

        // Side by side viewer with CustomPainter
        Container(
          height: 280,
          decoration: BoxDecoration(
            color: LunarTheme.background,
            borderRadius: const BorderRadius.vertical(bottom: Radius.circular(8)),
            border: Border.all(color: LunarTheme.border),
          ),
          clipBehavior: Clip.antiAlias,
          child: InteractiveViewer(
            minScale: 0.7,
            maxScale: 4.0,
            child: LayoutBuilder(
              builder: (context, constraints) {
                final totalWidth = constraints.maxWidth;
                final totalHeight = constraints.maxHeight;
                final halfWidth = totalWidth / 2.0;

                return Stack(
                  fit: StackFit.expand,
                  children: [
                    // Left: Reference Image
                    Positioned(
                      left: 0,
                      top: 0,
                      bottom: 0,
                      width: halfWidth,
                      child: Container(
                        decoration: const BoxDecoration(
                          border: Border(right: BorderSide(color: LunarTheme.border, width: 1)),
                        ),
                        child: widget.refImageWidget,
                      ),
                    ),

                    // Right: Moving Image
                    Positioned(
                      left: halfWidth,
                      top: 0,
                      bottom: 0,
                      width: halfWidth,
                      child: widget.movImageWidget,
                    ),

                    // Correspondence Lines Overlay
                    Positioned.fill(
                      child: CustomPaint(
                        painter: MatchLinesPainter(
                          matches: displayMatches,
                          refWidth: widget.refWidth,
                          refHeight: widget.refHeight,
                          totalWidth: totalWidth,
                          totalHeight: totalHeight,
                          halfWidth: halfWidth,
                        ),
                      ),
                    ),

                    // Labels Overlay
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.75),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: LunarTheme.borderLight),
                        ),
                        child: const Text("REFERENCE (FIXED)", style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: Colors.white)),
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.75),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: LunarTheme.borderLight),
                        ),
                        child: const Text("MOVING (WARPED)", style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: Colors.white)),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTab(MatchFilterTab tab, String label) {
    final isSelected = _activeTab == tab;
    return InkWell(
      onTap: () => setState(() => _activeTab = tab),
      borderRadius: BorderRadius.circular(4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: isSelected ? Colors.white : Colors.transparent,
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.5,
            color: isSelected ? Colors.black : LunarTheme.textSecondary,
          ),
        ),
      ),
    );
  }
}

class MatchLinesPainter extends CustomPainter {
  final List<MatchPairModel> matches;
  final int refWidth;
  final int refHeight;
  final double totalWidth;
  final double totalHeight;
  final double halfWidth;

  MatchLinesPainter({
    required this.matches,
    required this.refWidth,
    required this.refHeight,
    required this.totalWidth,
    required this.totalHeight,
    required this.halfWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (refWidth == 0 || refHeight == 0) return;

    final scaleXRef = halfWidth / refWidth;
    final scaleYRef = totalHeight / refHeight;
    final scaleRef = scaleXRef < scaleYRef ? scaleXRef : scaleYRef;
    final offXRef = (halfWidth - (refWidth * scaleRef)) / 2.0;
    final offYRef = (totalHeight - (refHeight * scaleRef)) / 2.0;

    final inlierPaint = Paint()
      ..color = Colors.white.withOpacity(0.80)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    final outlierPaint = Paint()
      ..color = LunarTheme.border.withOpacity(0.40)
      ..strokeWidth = 0.8
      ..style = PaintingStyle.stroke;

    final dotPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    for (final m in matches) {
      final p1 = Offset(
        offXRef + (m.refPt[0] * scaleRef),
        offYRef + (m.refPt[1] * scaleRef),
      );
      final p2 = Offset(
        halfWidth + offXRef + (m.movPt[0] * scaleRef),
        offYRef + (m.movPt[1] * scaleRef),
      );

      final paint = m.isInlier ? inlierPaint : outlierPaint;
      canvas.drawLine(p1, p2, paint);

      canvas.drawCircle(p1, 2.0, dotPaint);
      canvas.drawCircle(p2, 2.0, dotPaint);
    }
  }

  @override
  bool shouldRepaint(covariant MatchLinesPainter oldDelegate) {
    return oldDelegate.matches != matches || oldDelegate.totalWidth != totalWidth;
  }
}
