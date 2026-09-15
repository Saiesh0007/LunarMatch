import 'package:flutter/material.dart';
import '../app/theme.dart';

class StatusBadge extends StatelessWidget {
  final String mode;

  const StatusBadge({
    super.key,
    required this.mode,
  });

  @override
  Widget build(BuildContext context) {
    String displayMode = mode;
    if (displayMode.toUpperCase().contains("OFFLINE")) {
      displayMode = "Offline";
    } else if (displayMode.toUpperCase().contains("SIMULATION")) {
      displayMode = "Simulation";
    } else if (displayMode.toUpperCase().contains("LIVE")) {
      displayMode = "Live";
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceElevated,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: LunarTheme.borderLight, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 1.2),
              color: Colors.transparent,
            ),
          ),
          const SizedBox(width: 5),
          Flexible(
            child: Text(
              displayMode,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.6,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
