import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../providers/pipeline_provider.dart';
import '../services/api_service.dart';

class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  late TextEditingController _urlController;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: apiService.baseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("ABOUT SPECTRUM"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 42,
                          height: 42,
                          decoration: BoxDecoration(
                            color: LunarTheme.surfaceElevated,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: LunarTheme.borderLight),
                          ),
                          child: const Icon(Icons.satellite_alt_outlined, color: Colors.white, size: 22),
                        ),
                        const SizedBox(width: 14),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "SPECTRUM",
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 1.5,
                                  color: Colors.white,
                                ),
                              ),
                              Text(
                                "LunarMatch Multi-Modal Correspondence Engine",
                                style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Divider(height: 1),
                    const SizedBox(height: 14),
                    _buildMetaRow("Target Event", "Smart India Hackathon 2026"),
                    _buildMetaRow("Problem Statement", "PS 26166"),
                    _buildMetaRow("Lead Organization", "ISRO (Indian Space Research Organisation)"),
                    _buildMetaRow("Development Team", "Team Spectrum"),
                    _buildMetaRow("Domain", "Space Technology"),
                    _buildMetaRow("Architecture Version", "v1.0.0-mvp (Baseline + Simulation)"),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Non-negotiable engineering principles
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "NON-NEGOTIABLE ENGINEERING PRINCIPLES",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildPrincipleItem(
                      "Rule A — Scientific Honesty",
                      "Never claim algorithms or sub-pixel accuracy that were not actually tested. Delineates IMPLEMENTED from SIMULATED research models.",
                    ),
                    _buildPrincipleItem(
                      "Rule B — Zero Fake Metrics",
                      "All RMSE, inlier counts, inlier ratios, and coverage metrics originate from real OpenCV execution or deterministic mathematical simulation (Seed 26166).",
                    ),
                    _buildPrincipleItem(
                      "Rule C — Terminology Preservation",
                      "Strict adherence to 'Reference Image' (Fixed Coordinate System) and 'Moving Image' (Image to Transform).",
                    ),
                    _buildPrincipleItem(
                      "Rule D — Fail-Safe Registration",
                      "Unsuitable image pairs are declared 'REGISTRATION NOT RELIABLE' with explicit diagnostic reasons, preventing distorted or misleading warps.",
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // API Configuration Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "BACKEND API CONNECTION",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      "Configure FastAPI backend host URL. Useful when connecting physical Android devices via local WiFi / LAN.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _urlController,
                      style: LunarTheme.mono.copyWith(fontSize: 12, color: Colors.white),
                      decoration: InputDecoration(
                        labelText: "API Base URL",
                        labelStyle: const TextStyle(color: LunarTheme.textTertiary, fontSize: 12),
                        isDense: true,
                        filled: true,
                        fillColor: LunarTheme.surfaceElevated,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(6),
                          borderSide: const BorderSide(color: LunarTheme.border),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(6),
                          borderSide: const BorderSide(color: LunarTheme.border),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(6),
                          borderSide: const BorderSide(color: Colors.white),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    LayoutBuilder(
                      builder: (context, constraints) {
                        final isVeryNarrow = constraints.maxWidth < 260;

                        final saveBtn = ElevatedButton.icon(
                          onPressed: () {
                            apiService.setBaseUrl(_urlController.text.trim());
                            pipeProv.checkBackendHealth();
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text("API Base URL updated")),
                            );
                          },
                          icon: const Icon(Icons.save_outlined, size: 16),
                          label: const Text("SAVE URL"),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 8),
                            backgroundColor: Colors.white,
                            foregroundColor: Colors.black,
                          ),
                        );

                        final demoBtn = OutlinedButton.icon(
                          onPressed: () {
                            pipeProv.toggleLocalDemoMode(!pipeProv.forceLocalDemo);
                          },
                          icon: Icon(
                            pipeProv.forceLocalDemo ? Icons.toggle_on : Icons.toggle_off,
                            size: 18,
                            color: Colors.white,
                          ),
                          label: Text(
                            pipeProv.forceLocalDemo ? "DEMO FORCED" : "ALLOW LIVE",
                            style: const TextStyle(fontSize: 11),
                          ),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 8),
                            foregroundColor: Colors.white,
                            side: const BorderSide(color: LunarTheme.borderLight),
                          ),
                        );

                        if (isVeryNarrow) {
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              saveBtn,
                              const SizedBox(height: 8),
                              demoBtn,
                            ],
                          );
                        }

                        return Row(
                          children: [
                            Expanded(child: saveBtn),
                            const SizedBox(width: 8),
                            Expanded(child: demoBtn),
                          ],
                        );
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetaRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: LunarTheme.textTertiary)),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPrincipleItem(String title, String desc) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
          const SizedBox(height: 2),
          Text(desc, style: const TextStyle(fontSize: 10, color: LunarTheme.textSecondary, height: 1.35)),
        ],
      ),
    );
  }
}
