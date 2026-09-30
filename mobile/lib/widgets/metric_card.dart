import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../utils/animation_utils.dart';

class MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final IconData? icon;
  final Color? accentColor;
  final double? countUpValue;
  final String Function(double)? countUpFormatter;

  const MetricCard({
    super.key,
    required this.title,
    required this.value,
    this.subtitle,
    this.icon,
    this.accentColor,
    this.countUpValue,
    this.countUpFormatter,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Text(
                  title.toUpperCase(),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 9.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                    color: LunarTheme.textTertiary,
                  ),
                ),
              ),
              if (icon != null) ...[
                const SizedBox(width: 4),
                Icon(icon, size: 14, color: LunarTheme.textTertiary),
              ],
            ],
          ),
          const SizedBox(height: 6),
          _buildValue(context),
          if (subtitle != null) ...[
            const SizedBox(height: 3),
            Text(
              subtitle!,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10,
                color: LunarTheme.textTertiary,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildValue(BuildContext context) {
    if (countUpValue != null &&
        !AnimationUtils.isReducedMotion(context) &&
        !AnimationUtils.isRunningInTest) {
      return TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0.0, end: countUpValue!),
        duration: const Duration(milliseconds: 500),
        curve: Curves.easeOut,
        builder: (context, val, _) {
          final display = countUpFormatter != null
              ? countUpFormatter!(val)
              : val.toInt().toString();
          return Text(
            display,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontFamily: 'Courier',
              fontFamilyFallback: ['monospace'],
              fontSize: 17,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.5,
              color: Colors.white,
            ),
          );
        },
      );
    }
    return Text(
      value,
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: const TextStyle(
        fontFamily: 'Courier',
        fontFamilyFallback: ['monospace'],
        fontSize: 17,
        fontWeight: FontWeight.w800,
        letterSpacing: 0.5,
        color: Colors.white,
      ),
    );
  }
}
