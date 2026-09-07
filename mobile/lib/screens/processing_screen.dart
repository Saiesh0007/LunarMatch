import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../providers/pipeline_provider.dart';
import '../widgets/pipeline_step.dart';

class ProcessingScreen extends StatelessWidget {
  const ProcessingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final stages = pipeProv.currentStages;

    final completedCount = stages.where((s) => s.status == "COMPLETED").length;
    final totalCount = stages.isEmpty ? 10 : stages.length;
    final progressFraction = completedCount / totalCount;

    final isDone = pipeProv.status == PipelineExecutionStatus.completed;
    final isError = pipeProv.status == PipelineExecutionStatus.error;

    return PopScope(
      canPop: isDone || isError,
      child: Scaffold(
        backgroundColor: LunarTheme.background,
        appBar: AppBar(
          title: const Text("PIPELINE EXECUTION"),
          automaticallyImplyLeading: isDone || isError,
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header Progress Status Card
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: isDone ? Colors.white : (isError ? LunarTheme.borderFocus : LunarTheme.border),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              isDone
                                  ? "PIPELINE COMPLETED"
                                  : (isError ? "EXECUTION FAILED" : "PROCESSING LUNAR IMAGES..."),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.8,
                                color: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            "${(progressFraction * 100).toInt()}%",
                            style: LunarTheme.mono.copyWith(fontSize: 12),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: progressFraction,
                          minHeight: 5,
                          backgroundColor: LunarTheme.surfaceElevated,
                          valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isDone
                            ? "Registration telemetry ready for inspection."
                            : (isError
                                ? (pipeProv.errorMessage ?? "Pipeline encountered an error")
                                : "Executing coordinate alignment and spatial balancing stages..."),
                        style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Stages List
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: LunarTheme.border),
                    ),
                    child: ListView.separated(
                      itemCount: stages.length,
                      separatorBuilder: (context, index) => const Divider(height: 1),
                      itemBuilder: (context, idx) {
                        return PipelineStepWidget(
                          stage: stages[idx],
                          isLast: idx == stages.length - 1,
                        );
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Action Button
                if (isDone)
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushReplacementNamed(context, AppRoutes.results);
                    },
                    icon: const Icon(Icons.analytics_outlined, size: 18),
                    label: const Text("VIEW REGISTRATION RESULT"),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                    ),
                  )
                else if (isError)
                  OutlinedButton.icon(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.arrow_back, size: 16),
                    label: const Text("BACK TO CONFIGURATION"),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: LunarTheme.borderLight),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
