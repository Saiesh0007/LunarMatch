import 'package:flutter/material.dart';
import '../app/theme.dart';

enum BadgeVariant { standard, outline, elevated, subtle }

/// Reusable, auto-sizing, responsive monochrome badge
/// Never overflows or clips text; gracefully wraps if horizontal space is constrained.
class ResponsiveBadge extends StatelessWidget {
  final String label;
  final IconData? icon;
  final BadgeVariant variant;
  final double fontSize;
  final EdgeInsetsGeometry padding;

  const ResponsiveBadge({
    super.key,
    required this.label,
    this.icon,
    this.variant = BadgeVariant.standard,
    this.fontSize = 9.0,
    this.padding = const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color border;
    Color text;

    switch (variant) {
      case BadgeVariant.standard:
        bg = LunarTheme.surfaceElevated;
        border = LunarTheme.borderLight;
        text = Colors.white;
        break;
      case BadgeVariant.outline:
        bg = Colors.transparent;
        border = LunarTheme.border;
        text = Colors.white;
        break;
      case BadgeVariant.elevated:
        bg = LunarTheme.surfaceElevated;
        border = LunarTheme.borderLight;
        text = Colors.white;
        break;
      case BadgeVariant.subtle:
        bg = LunarTheme.surfaceCard;
        border = LunarTheme.border;
        text = LunarTheme.textSecondary;
        break;
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        return Container(
          constraints: BoxConstraints(
            maxWidth: constraints.maxWidth.isFinite ? constraints.maxWidth : double.infinity,
          ),
          padding: padding,
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: border, width: 1),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: fontSize + 3, color: text),
                const SizedBox(width: 4),
              ],
              Flexible(
                child: Text(
                  label,
                  softWrap: true,
                  style: TextStyle(
                    fontSize: fontSize,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.6,
                    color: text,
                    height: 1.2,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
