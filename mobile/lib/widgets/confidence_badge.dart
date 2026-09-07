import 'package:flutter/material.dart';
import '../app/theme.dart';

class ConfidenceBadge extends StatelessWidget {
  final String level; // "HIGH", "MEDIUM", "LOW", "REJECTED"
  final double score;

  const ConfidenceBadge({
    super.key,
    required this.level,
    this.score = 0.0,
  });

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color border;
    Color fg;

    switch (level.toUpperCase()) {
      case 'HIGH':
        icon = Icons.verified_outlined;
        border = Colors.white;
        fg = Colors.white;
        break;
      case 'MEDIUM':
        icon = Icons.check_circle_outline;
        border = LunarTheme.borderFocus;
        fg = LunarTheme.textPrimary;
        break;
      case 'LOW':
        icon = Icons.warning_amber_rounded;
        border = LunarTheme.borderLight;
        fg = LunarTheme.textSecondary;
        break;
      default: // REJECTED / UNRELIABLE
        icon = Icons.error_outline;
        border = LunarTheme.borderLight;
        fg = LunarTheme.textSecondary;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceElevated,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: border, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: fg),
          const SizedBox(width: 5),
          Text(
            "CONFIDENCE: $level",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.6,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }
}
