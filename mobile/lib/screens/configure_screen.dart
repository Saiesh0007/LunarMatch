import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/pipeline_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';

class ConfigureScreen extends StatefulWidget {
  const ConfigureScreen({super.key});

  @override
  State<ConfigureScreen> createState() => _ConfigureScreenState();
}

class _ConfigureScreenState extends State<ConfigureScreen> {
  late PipelineConfigModel _config;
  int _computeMode = 0; // 0: Fast CPU, 1: Accurate Hybrid, 2: GPU Mode (disabled)

  @override
  void initState() {
    super.initState();
    final pipeProv = context.read<PipelineProvider>();
    _config = PipelineConfigModel(
      featureMethod: pipeProv.config.featureMethod,
      matcher: pipeProv.config.matcher,
      ratioThreshold: pipeProv.config.ratioThreshold,
      geometricModel: pipeProv.config.geometricModel,
      estimatorMethod: pipeProv.config.estimatorMethod,
      subpixelRefinement: pipeProv.config.subpixelRefinement,
      spatialBalancing: pipeProv.config.spatialBalancing,
      gridSize: pipeProv.config.gridSize,
      maxPerCell: pipeProv.config.maxPerCell,
      ransacThreshold: pipeProv.config.ransacThreshold,
      maxFeatures: pipeProv.config.maxFeatures,
      preprocessing: PreprocessingConfigModel(
        normalize: pipeProv.config.preprocessing.normalize,
        clahe: pipeProv.config.preprocessing.clahe,
        denoise: pipeProv.config.preprocessing.denoise,
      ),
      simulationMode: pipeProv.config.simulationMode,
      failSafeOverride: pipeProv.config.failSafeOverride,
    );
  }

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Pipeline Configuration"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Segmented control
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SegmentedButton<int>(
                  segments: const [
                    ButtonSegment(value: 0, label: Text("Fast", style: TextStyle(fontSize: 12)), tooltip: "Fast CPU"),
                    ButtonSegment(value: 1, label: Text("Accurate", style: TextStyle(fontSize: 12)), tooltip: "Accurate Hybrid"),
                    ButtonSegment(value: 2, label: Text("GPU", style: TextStyle(fontSize: 12)), enabled: false, tooltip: "GPU Mode (disabled)"),
                  ],
                  selected: {_computeMode},
                  onSelectionChanged: (Set<int> newSelection) {
                    setState(() {
                      _computeMode = newSelection.first;
                    });
                  },
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.resolveWith<Color>((states) {
                      if (states.contains(WidgetState.selected)) {
                        return LunarTheme.primary;
                      }
                      if (states.contains(WidgetState.disabled)) {
                        return LunarTheme.surfaceElevated;
                      }
                      return LunarTheme.surfaceCard;
                    }),
                    foregroundColor: WidgetStateProperty.resolveWith<Color>((states) {
                      if (states.contains(WidgetState.selected)) {
                        return Colors.black;
                      }
                      if (states.contains(WidgetState.disabled)) {
                        return LunarTheme.textTertiary;
                      }
                      return LunarTheme.textPrimary;
                    }),
                    side: WidgetStateProperty.all(BorderSide(color: LunarTheme.border, width: 1)),
                    shape: WidgetStateProperty.all(
                      RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Dropdowns
              _buildDropdownSection(
                title: "Feature Method",
                value: _config.featureMethod,
                items: ["SIFT", "RIFT2", "SuperPoint"],
                onChanged: (v) {
                  setState(() {
                    _config.featureMethod = v!;
                    _config.simulationMode = false;
                  });
                },
              ),
              const SizedBox(height: 16),

              _buildDropdownSection(
                title: "Matcher",
                value: _config.matcher,
                items: ["BF", "FLANN"],
                onChanged: (v) => setState(() => _config.matcher = v!),
              ),
              const SizedBox(height: 16),

              _buildDropdownSection(
                title: "Geometric Model",
                value: _config.geometricModel,
                items: ["homography", "affine"],
                onChanged: (v) => setState(() => _config.geometricModel = v!),
              ),
              const SizedBox(height: 16),

              _buildDropdownSection(
                title: "Estimator",
                value: _config.estimatorMethod,
                items: ["magsac", "ransac"],
                onChanged: (v) => setState(() => _config.estimatorMethod = v!),
              ),
              const SizedBox(height: 24),

              // Toggle rows
              _buildToggleRow(
                title: "Sub-pixel Refinement",
                value: _config.subpixelRefinement,
                onChanged: (v) => setState(() => _config.subpixelRefinement = v),
              ),
              const SizedBox(height: 12),
              _buildToggleRow(
                title: "Uniform Grid Balancing",
                value: _config.spatialBalancing,
                onChanged: (v) => setState(() => _config.spatialBalancing = v),
              ),
              const SizedBox(height: 12),
              _buildToggleRow(
                title: "Sub-pixel refinement",
                value: true,
                onChanged: (v) {},
              ),
              const SizedBox(height: 24),

              // Advanced Parameters Collapsible
              Theme(
                data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                child: ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  title: const Text(
                    "Advanced Parameters",
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: LunarTheme.textPrimary,
                    ),
                  ),
                  iconColor: LunarTheme.textPrimary,
                  collapsedIconColor: LunarTheme.textSecondary,
                  children: [
                    _buildSliderRow(
                      title: "Lowe's Ratio Threshold",
                      value: _config.ratioThreshold,
                      min: 0.50,
                      max: 0.90,
                      displayStr: _config.ratioThreshold.toStringAsFixed(2),
                      onChanged: (v) => setState(() => _config.ratioThreshold = v),
                    ),
                    _buildSliderRow(
                      title: "RANSAC Threshold",
                      value: _config.ransacThreshold,
                      min: 1.0,
                      max: 8.0,
                      displayStr: "${_config.ransacThreshold.toStringAsFixed(1)} px",
                      onChanged: (v) => setState(() => _config.ransacThreshold = v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // Run Registration button
              ElevatedButton(
                onPressed: () {
                  pipeProv.updateConfig(_config);
                  final ref = imgProv.referenceImage!;
                  final mov = imgProv.movingImage!;
                  pipeProv.runRegistration(
                    refImage: ref,
                    movImage: mov,
                    refSensor: imgProv.referenceSensor,
                    movSensor: imgProv.movingSensor,
                    pairId: imgProv.selectedDemoPair?.pairId,
                  );
                  Navigator.pushNamed(context, AppRoutes.processing);
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
                child: const Text("Run Registration"),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDropdownSection({
    required String title,
    required String value,
    required List<String> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: LunarTheme.textSecondary,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            color: LunarTheme.surfaceElevated,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: LunarTheme.border),
          ),
          child: DropdownButtonHideUnderline(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: double.infinity),
              child: DropdownButton<String>(
                value: value,
                isExpanded: true,
                dropdownColor: LunarTheme.surfaceElevated,
                icon: const Icon(Icons.arrow_drop_down, color: LunarTheme.textPrimary),
                style: const TextStyle(
                  fontSize: 14,
                  color: LunarTheme.textPrimary,
                  fontWeight: FontWeight.w500,
                  overflow: TextOverflow.ellipsis,
                ),
                items: items.map((e) {
                  String label = e;
                  if (e == 'SIFT') label = 'SIFT Baseline';
                  if (e == 'RIFT2') label = 'RIFT2 Multiscale';
                  if (e == 'BF') label = 'BF + Ratio Test';
                  if (e == 'homography') label = 'MAGSAC++ (Homography)';
                  return DropdownMenuItem(value: e, child: Text(label, overflow: TextOverflow.ellipsis));
                }).toList(),
                onChanged: onChanged,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildToggleRow({
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Flexible(
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 13,
              color: LunarTheme.textPrimary,
              fontWeight: FontWeight.w600,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 12),
        Switch(
          value: value,
          activeColor: Colors.black,
          activeTrackColor: LunarTheme.primary,
          inactiveThumbColor: LunarTheme.textSecondary,
          inactiveTrackColor: LunarTheme.surfaceElevated,
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildSliderRow({
    required String title,
    required double value,
    required double min,
    required double max,
    required String displayStr,
    required ValueChanged<double> onChanged,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12, top: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: LunarTheme.textSecondary,
                ),
              ),
              Text(
                displayStr,
                style: LunarTheme.mono.copyWith(fontSize: 12),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: LunarTheme.primary,
              thumbColor: LunarTheme.primary,
              inactiveTrackColor: LunarTheme.surfaceElevated,
            ),
            child: Slider(
              value: value,
              min: min,
              max: max,
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}