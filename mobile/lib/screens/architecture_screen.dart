import 'package:flutter/material.dart';
import '../app/theme.dart';

class ArchitectureScreen extends StatefulWidget {
  const ArchitectureScreen({super.key});

  @override
  State<ArchitectureScreen> createState() => _ArchitectureScreenState();
}

class _ArchitectureScreenState extends State<ArchitectureScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("SYSTEM ARCHITECTURE"),
      ),
      body: SafeArea(
        child:790
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Pipeline",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      "Multi-modal ingestion through feature extraction, matching, geometric verification, and quality assessment.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.45),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              ..._buildPipeline(),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildPipeline() {
    final stages = [
      ("01", "Multi-modal Ingestion", "Ingests optical (OHRC, TMC-2), hyperspectral (IIRS), and reference (LRO NAC, SELENE) imagery."),
      ("02", "Preprocessing", "Radiometric normalization, shadow masking, and illumination correction."),
      ("03", "Feature Extraction", "RIFT2 phase-congruency descriptors for illumination-invariant matching."),
      ("04", "Robust Estimation", "MAGSAC++ threshold-free model fitting with automatic outlier rejection."),
      ("05", "Sub-pixel Refinement", "Phase-correlation refinement with uniform spatial grid balancing."),
    ];

    final widgets = <Widget>[];

    for (int i = 0; i < stages.length; i++) {
      final (num, title, desc) = stages[i];

      widgets.add(
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: LunarTheme.surfaceCard,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: LunarTheme.border),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 32,
                height: 28,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: LunarTheme.borderLight),
                ),
                child: Text(
                  num,
                  style: LunarTheme.mono.copyWith(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 11.5,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.6,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      desc,
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );

      if (i < stages.length - 1) {
        widgets.add(
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 4),
            child: Center(
              child: Icon(Icons.arrow_downward, size: 14, color: LunarTheme.textTertiary),
            ),
          ),
        );
      }
    }

    return widgets;
  }
}

