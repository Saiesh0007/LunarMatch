import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/pipeline_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';
import '../widgets/section_header.dart';
import '../utils/animation_utils.dart';

class ConfigureScreen extends StatefulWidget {
  const ConfigureScreen({super.key});

  @override
  State<ConfigureScreen> createState() => _ConfigureScreenState();
}

class _ConfigureScreenState extends State<ConfigureScreen> {
  late PipelineConfigModel _config;

  @override
  void initState() {
    super.initState();
    // Clone config from provider
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
    final animTarget = AnimationUtils.targetFor(context);

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("PIPELINE CONFIGURATION"),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _config = PipelineConfigModel();
              });
            },
            child: const Text("RESET", style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Section 1: Feature Extraction Method
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionHeader(
                    title: "01 FEATURE EXTRACTION METHOD",
                    subtitle: "Select feature extraction technique",
                  ),
                  _buildMethodRadio("SIFT", "OpenCV SIFT Baseline"),
                  _buildMethodRadio("RIFT2", "Radiation-Invariant Phase Feature    [DEFAULT]"),
                  _buildMethodRadio("SuperPoint", "Learned Deep Feature Extractor"),
                  _buildMethodRadio("superglue", "Sinkhorn Optimal-Transport Matcher"),
                  if (_config.featureMethod == "SuperPoint")
                    _buildWarningBanner(
                      "Warning: SuperPoint extraction on CPU takes 3-5 seconds per "
                      "image (6-10 seconds for a pair). The default RIFT2 extractor "
                      "runs in under 5 seconds total.",
                    ),
                ],
              )
                  .animate(target: animTarget)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Section 2: Correspondence Matcher
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionHeader(
                    title: "02 MATCHING ALGORITHM",
                    subtitle: "Select 2-NN descriptor correspondence strategy",
                  ),
                  Row(
                    children: [
                      Expanded(
                        child: _buildChoiceChip("BF (Brute-Force)", _config.matcher == "BF", () {
                          setState(() => _config.matcher = "BF");
                        }),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildChoiceChip("FLANN (KD-Tree)", _config.matcher == "FLANN", () {
                          setState(() => _config.matcher = "FLANN");
                        }),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: _buildChoiceChip("SuperGlue", _config.matcher == "SuperGlue", () {
                          setState(() => _config.matcher = "SuperGlue");
                        }),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildChoiceChip("LightGlue", _config.matcher == "LightGlue", () {
                          setState(() => _config.matcher = "LightGlue");
                        }),
                      ),
                    ],
                  ),
                  if (_config.matcher == "SuperGlue")
                    _buildWarningBanner(
                      "Warning: SuperGlue inference on CPU takes 8-15 seconds per "
                      "pair and may exceed the demo budget. Benchmarked success rate "
                      "on this fixture was 0%.",
                    ),
                  if (_config.matcher == "LightGlue")
                    _buildWarningBanner(
                      "Warning: LightGlue inference on CPU takes 5-8 seconds per "
                      "pair. Benchmarked success rate on this fixture was 0%.",
                    ),
                ],
              )
                  .animate(target: animTarget, delay: 80.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Section 3: Preprocessing
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionHeader(
                    title: "03 PREPROCESSING FILTERS",
                    subtitle: "Radiometric enhancement for high-contrast lunar shadow/crest zones",
                  ),
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeInOut,
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: (_config.preprocessing.normalize || _config.preprocessing.clahe || _config.preprocessing.denoise)
                            ? Colors.white
                            : LunarTheme.border,
                      ),
                    ),
                    child: Column(
                      children: [
                        CheckboxListTile(
                          title: const Text("Intensity Normalization", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                          subtitle: const Text("Dynamic range stretching to [0, 255]", style: TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
                          value: _config.preprocessing.normalize,
                          activeColor: Colors.white,
                          checkColor: Colors.black,
                          onChanged: (v) => setState(() => _config.preprocessing.normalize = v ?? true),
                        ),
                        const Divider(height: 1),
                        CheckboxListTile(
                          title: const Text("CLAHE (Adaptive Histogram)", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                          subtitle: const Text("Reveals subtle regolith textures in deep shadows", style: TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
                          value: _config.preprocessing.clahe,
                          activeColor: Colors.white,
                          checkColor: Colors.black,
                          onChanged: (v) => setState(() => _config.preprocessing.clahe = v ?? true),
                        ),
                        const Divider(height: 1),
                        CheckboxListTile(
                          title: const Text("Edge-Preserving Denoising", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                          subtitle: const Text("Suppresses sensor noise without blurring crater rims", style: TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
                          value: _config.preprocessing.denoise,
                          activeColor: Colors.white,
                          checkColor: Colors.black,
                          onChanged: (v) => setState(() => _config.preprocessing.denoise = v ?? true),
                        ),
                      ],
                    ),
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 160.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Section 4: Spatial Grid Balancing
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionHeader(
                    title: "04 SPATIAL BALANCING",
                    subtitle: "Eliminates crater rim clustering across N x N spatial grid",
                  ),
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeInOut,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: _config.spatialBalancing ? Colors.white : LunarTheme.border,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Expanded(
                              child: Text(
                                "Enable Spatial Balancing",
                                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Switch(
                              value: _config.spatialBalancing,
                              activeThumbColor: Colors.white,
                              onChanged: (v) => setState(() => _config.spatialBalancing = v),
                            ),
                          ],
                        ),
                        if (_config.spatialBalancing) ...[
                          const SizedBox(height: 8),
                          Wrap(
                            crossAxisAlignment: WrapCrossAlignment.center,
                            spacing: 8,
                            runSpacing: 6,
                            children: [
                              const Text("Grid Partitioning:", style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary)),
                              _buildGridButton(4),
                              _buildGridButton(6),
                              _buildGridButton(8),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 240.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Section 5: Geometric Model & Estimator
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionHeader(
                    title: "05 GEOMETRIC MODEL & ESTIMATOR",
                    subtitle: "Transformation degrees of freedom & robust estimator",
                  ),
                  Row(
                    children: [
                      Expanded(
                        child: _buildChoiceChip("HOMOGRAPHY (8-DOF)", _config.geometricModel == "homography", () {
                          setState(() => _config.geometricModel = "homography");
                        }),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildChoiceChip("AFFINE (6-DOF)", _config.geometricModel == "affine", () {
                          setState(() => _config.geometricModel = "affine");
                        }),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildChoiceChip("MAGSAC++", _config.estimatorMethod == "magsac", () {
                          setState(() => _config.estimatorMethod = "magsac");
                        }),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _buildChoiceChip("RANSAC", _config.estimatorMethod == "ransac", () {
                          setState(() => _config.estimatorMethod = "ransac");
                        }),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeInOut,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: _config.subpixelRefinement ? Colors.white : LunarTheme.border,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Expanded(
                          child: Text("Sub-pixel Refinement", style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                        ),
                        const SizedBox(width: 8),
                        Switch(
                          value: _config.subpixelRefinement,
                          activeThumbColor: Colors.white,
                          onChanged: (v) => setState(() => _config.subpixelRefinement = v),
                        ),
                      ],
                    ),
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 320.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Section 6: Sliders & Fail-safe Verification Toggle
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
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
                    title: "RANSAC Inlier Threshold",
                    value: _config.ransacThreshold,
                    min: 1.0,
                    max: 8.0,
                    displayStr: "${_config.ransacThreshold.toStringAsFixed(1)} px",
                    onChanged: (v) => setState(() => _config.ransacThreshold = v),
                  ),
                  const SizedBox(height: 12),
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeInOut,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: LunarTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: _config.failSafeOverride ? Colors.white : LunarTheme.border,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("Fail-Safe Rejection Override", style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
                              Text("Forces fail-safe trigger for unaligned image pairs", style: TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Switch(
                          value: _config.failSafeOverride,
                          activeThumbColor: Colors.white,
                          onChanged: (v) => setState(() => _config.failSafeOverride = v),
                        ),
                      ],
                    ),
                  ),
                ],
              )
                  .animate(target: animTarget, delay: 400.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 24),

              // Section 7: Run Button with Press Scale 95% -> 100% (150 ms)
              _RunPressButton(
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
              )
                  .animate(target: animTarget, delay: 480.ms)
                  .fadeIn(duration: 250.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWarningBanner(String message) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2000),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFFFB300), width: 1.0),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.warning_amber_rounded, color: Color(0xFFFFB300), size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                fontSize: 11,
                color: Color(0xFFFFD54F),
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMethodRadio(String value, String label) {
    final isSelected = _config.featureMethod == value;
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isSelected ? Colors.white : LunarTheme.border,
          width: isSelected ? 1.2 : 1.0,
        ),
      ),
      child: RadioListTile<String>(
        value: value,
        groupValue: _config.featureMethod,
        activeColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        onChanged: (val) {
          if (val != null) {
            setState(() {
              _config.featureMethod = val;
              _config.simulationMode = false;
            });
          }
        },
        title: Text(
          value,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.white),
        ),
        subtitle: Text(label, style: const TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
      ),
    );
  }

  Widget _buildChoiceChip(String label, bool isSelected, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 8),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : LunarTheme.surfaceCard,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isSelected ? Colors.white : LunarTheme.border,
          ),
        ),
        child: FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 10.5,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.4,
              color: isSelected ? Colors.black : LunarTheme.textSecondary,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGridButton(int size) {
    final isSelected = _config.gridSize == size;
    return InkWell(
      onTap: () => setState(() => _config.gridSize = size),
      borderRadius: BorderRadius.circular(4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : LunarTheme.surfaceElevated,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: isSelected ? Colors.white : LunarTheme.border,
          ),
        ),
        child: Text(
          "$size × $size",
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            color: isSelected ? Colors.black : Colors.white,
          ),
        ),
      ),
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
      margin: const EdgeInsets.only(bottom: 8),
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
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: LunarTheme.textSecondary),
                ),
              ),
              const SizedBox(width: 8),
              Text(displayStr, style: LunarTheme.mono.copyWith(fontSize: 11)),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: Colors.white,
              thumbColor: Colors.white,
              inactiveTrackColor: const Color(0xFF2E2E2E),
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

class _RunPressButton extends StatefulWidget {
  final VoidCallback onPressed;
  const _RunPressButton({required this.onPressed});

  @override
  State<_RunPressButton> createState() => _RunPressButtonState();
}

class _RunPressButtonState extends State<_RunPressButton> {
  double _scale = 1.0;

  @override
  Widget build(BuildContext context) {
    return Listener(
      onPointerDown: (_) => setState(() => _scale = 0.95),
      onPointerUp: (_) => setState(() => _scale = 1.0),
      onPointerCancel: (_) => setState(() => _scale = 1.0),
      child: AnimatedScale(
        scale: _scale,
        duration: const Duration(milliseconds: 150),
        curve: Curves.easeOut,
        child: ElevatedButton.icon(
          onPressed: widget.onPressed,
          icon: const Icon(Icons.rocket_launch_outlined, size: 18),
          label: const Text("RUN LUNARMATCH PIPELINE"),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            backgroundColor: Colors.white,
            foregroundColor: Colors.black,
          ),
        ),
      ),
    );
  }
}

