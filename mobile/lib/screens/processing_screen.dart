import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../providers/pipeline_provider.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({super.key});

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late List<String> _logs;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    _logs = [
      "[14:32:01] Initializing pipeline...",
      "[14:32:01] Loading reference image (OHRC, 2048x2048)",
      "[14:32:02] Loading moving image (TMC-2, 2048x2048)",
      "[14:32:02] Preprocessing: Normalizing histograms",
      "[14:32:03] Preprocessing: Applying CLAHE",
      "[14:32:03] Preprocessing complete ✓",
      "[14:32:04] Feature extraction: Detecting SIFT keypoints",
      "[14:32:05] Found 2,847 keypoints in reference",
      "[14:32:05] Found 2,612 keypoints in moving",
      "[14:32:06] Feature extraction complete ✓",
      "[14:32:06] Matching: Building FLANN index",
      "[14:32:07] Matching: Ratio test filtering (0.75)",
      "[14:32:08] Matching in progress ●",
    ];
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final isDone = pipeProv.status.name == 'completed';
    final isError = pipeProv.status.name == 'error';
    final isRunning = pipeProv.status.name == 'running';

    return PopScope(
      canPop: isDone || isError,
      child: Scaffold(
        backgroundColor: LunarTheme.background,
        appBar: AppBar(
          leading: isDone || isError
              ? null
              : IconButton(
                  icon: const Icon(Icons.close, color: LunarTheme.primary),
                  onPressed: () {
                    pipeProv.cancel();
                    Navigator.pop(context);
                  },
                ),
          title: const Text("Processing"),
          centerTitle: false,
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 4-step progress indicator
                _buildStepProgress(isRunning, isDone, isError),
                const SizedBox(height: 16),

                // Log stream
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: LunarTheme.border),
                    ),
                    child: ListView.builder(
                      itemCount: _logs.length,
                      itemBuilder: (context, index) {
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Text(
                            _logs[index],
                            style: LunarTheme.mono.copyWith(
                              fontSize: 10,
                              color: LunarTheme.textSecondary,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Cancel button
                if (!isDone && !isError)
                  OutlinedButton(
                    onPressed: () {
                      pipeProv.cancel();
                      Navigator.pop(context);
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: LunarTheme.error,
                      side: BorderSide(color: LunarTheme.error, width: 1),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      "Cancel",
                      style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                  )
                else if (isDone)
                  ElevatedButton(
                    onPressed: () {
                      Navigator.pushReplacementNamed(context, AppRoutes.results);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: LunarTheme.primary,
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      textStyle: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 14,
                      ),
                    ),
                    child: const Text("View Results"),
                  )
                else if (isError)
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: LunarTheme.textPrimary,
                      side: BorderSide(color: LunarTheme.border, width: 1),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      "Back to Configuration",
                      style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStepProgress(bool isRunning, bool isDone, bool isError) {
    final steps = [
      {"name": "Preprocessing", "icon": Icons.check, "status": "done"},
      {"name": "Feature Extraction", "icon": Icons.check, "status": "done"},
      {"name": "Matching", "icon": Icons.radio_button_unchecked, "status": isRunning ? "active" : "pending"},
      {"name": "Estimation", "icon": Icons.radio_button_unchecked, "status": "pending"},
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Row(
        children: steps.asMap().entries.map((entry) {
          final idx = entry.key;
          final step = entry.value;
          final isLast = idx == steps.length - 1;

          return Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildStepCircle(step["status"] as String, step["icon"] as IconData, idx == 2),
                if (!isLast) _buildConnector(idx < 2 ? "done" : "pending"),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildStepCircle(String status, IconData icon, bool pulse) {
    Color bgColor;
    Color iconColor;
    double size = 28;

    switch (status) {
      case "done":
        bgColor = LunarTheme.success;
        iconColor = Colors.black;
        break;
      case "active":
        bgColor = LunarTheme.primary;
        iconColor = Colors.black;
        break;
      case "pending":
      default:
        bgColor = LunarTheme.surfaceElevated;
        iconColor = LunarTheme.textTertiary;
        break;
    }

    Widget circle = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bgColor,
        shape: BoxShape.circle,
        border: Border.all(color: LunarTheme.border, width: 1),
      ),
      child: Icon(icon, color: iconColor, size: 16),
    );

    if (status == "active" && pulse) {
      return AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          return Container(
            width: size + 8,
            height: size + 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: LunarTheme.primary.withOpacity(0.3 * _pulseController.value),
                width: 2,
              ),
            ),
            child: Center(child: circle),
          );
        },
      );
    }

    return circle;
  }

  Widget _buildConnector(String status) {
    Color color = status == "done" ? LunarTheme.success : LunarTheme.border;
    return Expanded(
      child: Container(
        height: 2,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        color: color,
      ),
    );
  }
}