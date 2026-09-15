import 'package:flutter/material.dart';
import '../models/pipeline_model.dart';
import '../app/theme.dart';

class PipelineStepWidget extends StatelessWidget {
  final PipelineStageModel stage;
  final bool isLast;

  const PipelineStepWidget({
    super.key,
    required this.stage,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    Widget statusIcon;

    switch (stage.status.toUpperCase()) {
      case 'COMPLETED':
        statusColor = Colors.white;
        statusIcon = const Icon(Icons.check_circle, size: 18, color: Colors.white);
        break;
      case 'PROCESSING':
        statusColor = Colors.white;
        statusIcon = const SizedBox(
          width: 14,
          height: 14,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        );
        break;
      case 'FAILED':
        statusColor = LunarTheme.textTertiary;
        statusIcon = const Icon(Icons.cancel, size: 18, color: Colors.white);
        break;
      default: // PENDING / WAITING
        statusColor = LunarTheme.textTertiary;
        statusIcon = Container(
          width: 6,
          height: 6,
          decoration: const BoxDecoration(
            color: LunarTheme.border,
            shape: BoxShape.circle,
          ),
        );
    }

    final stageNumStr = stage.stageNumber.toString().padLeft(2, '0');

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Step number badge
          Container(
            width: 30,
            height: 24,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: LunarTheme.surfaceElevated,
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: stage.status == 'PROCESSING' ? Colors.white : LunarTheme.border,
              ),
            ),
            child: Text(
              stageNumStr,
              style: LunarTheme.mono.copyWith(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: statusColor,
              ),
            ),
          ),
          const SizedBox(width: 10),

          // Name and Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  stage.name,
                  style: TextStyle(
                    fontSize: 11.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.4,
                    color: stage.status == 'PENDING' ? LunarTheme.textTertiary : Colors.white,
                  ),
                ),
                if (stage.details != null && stage.status != 'PENDING') ...[
                  const SizedBox(height: 2),
                  Text(
                    stage.details!,
                    style: const TextStyle(fontSize: 10.5, color: LunarTheme.textSecondary),
                  ),
                ],
              ],
            ),
          ),

          // Duration if available
          if (stage.durationMs > 0 && stage.status == 'COMPLETED') ...[
            const SizedBox(width: 6),
            Text(
              "${stage.durationMs.toStringAsFixed(0)} ms",
              style: LunarTheme.mono.copyWith(fontSize: 10, color: LunarTheme.textTertiary),
            ),
            const SizedBox(width: 8),
          ],

          // Status Icon
          SizedBox(width: 22, child: Center(child: statusIcon)),
        ],
      ),
    );
  }
}
