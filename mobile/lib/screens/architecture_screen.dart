import 'package:flutter/material.dart';
import '../app/theme.dart';

class ArchitectureScreen extends StatefulWidget {
  const ArchitectureScreen({super.key});

  @override
  State<ArchitectureScreen> createState() => _ArchitectureScreenState();
}

class _ArchitectureScreenState extends State<ArchitectureScreen> {
  bool _showTargetArchitecture = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("SYSTEM ARCHITECTURE"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Architecture Switcher
              Container(
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: _buildArchTab(
                        "CURRENT MVP PIPELINE",
                        !_showTargetArchitecture,
                        () => setState(() => _showTargetArchitecture = false),
                      ),
                    ),
                    Expanded(
                      child: _buildArchTab(
                        "TARGET RESEARCH ARCHITECTURE",
                        _showTargetArchitecture,
                        () => setState(() => _showTargetArchitecture = true),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Overview Banner
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
                    Text(
                      _showTargetArchitecture ? "TARGET RESEARCH SPECIFICATION" : "OPERATIONAL BASELINE SPECIFICATION",
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _showTargetArchitecture
                          ? "Multi-stage deep neural and phase-congruency framework engineered for extreme multi-modal optical-to-radar correspondence (e.g. OHRC to Chandrayaan-2 Dual-Frequency SAR)."
                          : "Fully implemented, verifiable baseline using OpenCV SIFT, dual-pass Lowe ratio rejection, RANSAC projective estimation, and uniform spatial grid balancing.",
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.45),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Flow Diagram Blocks
              if (!_showTargetArchitecture) ..._buildMvpPipeline() else ..._buildTargetPipeline(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildArchTab(String title, bool isSelected, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          title,
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 9.5,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.4,
            color: isSelected ? Colors.black : LunarTheme.textTertiary,
          ),
        ),
      ),
    );
  }

  List<Widget> _buildMvpPipeline() {
    final stages = [
      ("01", "INPUT INGESTION & SENSOR LABELS", "Reference (Fixed) & Moving (Transformed) with sensor dropdown tagging (OHRC, TMC-2, IIRS, LRO NAC)."),
      ("02", "RADIOMETRIC PREPROCESSING", "Min-max normalization, Contrast Limited AHE (CLAHE) for crater shadow enhancement, bilateral edge denoising."),
      ("03", "FEATURE EXTRACTION (SIFT)", "OpenCV SIFT implementation extracting multiscale extrema keypoints and 128D orientation histograms."),
      ("04", "EXHAUSTIVE 2-NN MATCHING", "Brute-force L2 norm search across full descriptor hyperspace (or FLANN KD-Tree)."),
      ("05", "LOWE'S RATIO REJECTION", "Ambiguity pruning: retains correspondences with d1 < 0.75 * d2 to reject repetitive crater patterns."),
      ("06", "RANSAC PROJECTIVE CONSENSUS", "Estimates 8-DOF homography (or 6-DOF affine) with conditioning and determinant stability checks."),
      ("07", "SPATIAL GRID BALANCING", "Uniform N × N grid partitioning to prevent crater rim over-clustering and maximize coverage."),
      ("08", "FAIL-SAFE INTEGRITY EVALUATION", "Rejects pairs falling below threshold into 'REGISTRATION NOT RELIABLE' with technical diagnostics."),
      ("09", "COORDINATE WARPING & BLENDING", "Warp transformation, alpha blending overlay, and false-color difference map generation."),
      ("10", "MEASURED TELEMETRY & RUN AUDIT", "Directly measured reprojection RMSE and automatic persistence of 13 audit artifacts."),
    ];

    return _buildBlockList(stages);
  }

  List<Widget> _buildTargetPipeline() {
    final stages = [
      ("01", "MULTI-MODAL HETEROGENEOUS INGESTION", "Optical (OHRC/TMC-2), Hyperspectral (IIRS), and Chandrayaan-2 Dual-Frequency Synthetic Aperture Radar (DFSAR)."),
      ("02", "ADVANCED REGOLITH PREPROCESSING", "Shadow de-emphasis, radiometric cross-calibration, and DEM-guided slope illumination correction."),
      ("03", "PHASE CONGRUENCY / RIFT EXTRACTION", "Radiation-Invariant Feature Transform: phase congruency maps robust to radical radar-optical domain shifts."),
      ("04", "SUPERPOINT DEEP FEATURE DETECTOR", "Self-supervised learned keypoints trained on lunar surface topography with high repeatability."),
      ("05", "LIGHTGLUE DEEP ATTENTION MATCHER", "Transformer-based graph neural network performing contextual consensus matching with early stopping."),
      ("06", "RANSAC++ WITH DEM PRIOR CONSENSUS", "Topography-guided consensus estimation incorporating epipolar geometry and lunar digital elevation models."),
      ("07", "SUB-PIXEL PARALLAX REFINEMENT", "Gradient descent patch correlation achieving verified sub-pixel accuracy on lunar terrain features."),
      ("08", "NON-RIGID B-SPLINE LOCAL WARPING", "Thin-plate spline transformation addressing severe non-planar lunar topography distortions."),
      ("09", "FULL TELEMETRY VERIFICATION PIPELINE", "Ground-truth cross-validation, orthorectification check, and multi-sensor mosaic synthesis."),
    ];

    return _buildBlockList(stages);
  }

  List<Widget> _buildBlockList(List<(String, String, String)> stages) {
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
