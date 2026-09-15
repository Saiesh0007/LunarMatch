import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../models/capability_model.dart';
import '../services/api_service.dart';
import '../widgets/responsive_badge.dart';

class StatusScreen extends StatefulWidget {
  const StatusScreen({super.key});

  @override
  State<StatusScreen> createState() => _StatusScreenState();
}

class _StatusScreenState extends State<StatusScreen> {
  List<CapabilityItemModel> _capabilities = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadCapabilities();
  }

  Future<void> _loadCapabilities() async {
    try {
      final items = await apiService.fetchCapabilities();
      if (mounted) {
        setState(() {
          _capabilities = items;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _capabilities = _getStaticCapabilities();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("ENGINE CAPABILITIES"),
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
            : SingleChildScrollView(
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
                      child: const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "CAPABILITIES",
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 1.0,
                              color: Colors.white,
                            ),
                          ),
                          SizedBox(height: 6),
                          Text(
                            "LunarMatch's feature set covers the full registration pipeline: "
                            "feature detection, descriptor matching, geometric verification, "
                            "spatial balancing, and quality assessment.",
                            style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _capabilities.length,
                      itemBuilder: (context, idx) {
                        final item = _capabilities[idx];
                        return _buildCapabilityCard(item);
                      },
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildCapabilityCard(CapabilityItemModel item) {
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
          Wrap(
            alignment: WrapAlignment.spaceBetween,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 8,
            runSpacing: 6,
            children: [
              Text(
                item.name,
                style: const TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),
              ResponsiveBadge(
                label: item.status,
                variant: item.status == 'Active'
                    ? BadgeVariant.standard
                    : (item.status == 'Available' ? BadgeVariant.subtle : BadgeVariant.outline),
                fontSize: 8.5,
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            item.category.toUpperCase(),
            style: const TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.8,
              color: LunarTheme.textTertiary,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            item.notes,
            style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
          ),
        ],
      ),
    );
  }

  List<CapabilityItemModel> _getStaticCapabilities() {
    return const [
      CapabilityItemModel(
        name: "OpenCV SIFT Feature Detection & Description",
        status: "Active",
        category: "Vision Pipeline",
        notes: "OpenCV SIFT detector extracting keypoints and 128D orientation descriptors.",
      ),
      CapabilityItemModel(
        name: "Brute-Force 2-NN Matcher (L2 Norm)",
        status: "Active",
        category: "Vision Pipeline",
        notes: "Exhaustive nearest-neighbor matching across full descriptor hyperspace.",
      ),
      CapabilityItemModel(
        name: "Ambiguity Filter (d1 < 0.75 * d2)",
        status: "Active",
        category: "Vision Pipeline",
        notes: "Rejects ambiguous multi-crater matches via second-nearest neighbor ratio test.",
      ),
      CapabilityItemModel(
        name: "Projective Consensus Estimation",
        status: "Active",
        category: "Geometry",
        notes: "Planar projective model with stability conditioning and determinant validation.",
      ),
      CapabilityItemModel(
        name: "N x N Grid Balancing",
        status: "Active",
        category: "Spatial",
        notes: "Prevents crater rim keypoint clustering by capping top-k per spatial grid cell.",
      ),
      CapabilityItemModel(
        name: "Measured Pixel Residual Error",
        status: "Active",
        category: "Metrics",
        notes: "Directly measured RMSE across inliers. Defaults to N/A if unavailable.",
      ),
      CapabilityItemModel(
        name: "Deterministic Demo Engine",
        status: "Active",
        category: "Simulation",
        notes: "Fixed seed demo engine with physically coherent degradation curves.",
      ),
      CapabilityItemModel(
        name: "Fail-Safe Rejection Mechanism",
        status: "Active",
        category: "Safety",
        notes: "Rejects unreliable pairs with explicit technical diagnostic reasons.",
      ),
      CapabilityItemModel(
        name: "Radiation-Invariant Phase Feature",
        status: "Available",
        category: "Phase Features",
        notes: "Phase-congruency descriptor (216-D) for illumination-invariant matching.",
      ),
      CapabilityItemModel(
        name: "Deep Learned Feature Extractor",
        status: "Available",
        category: "Deep Models",
        notes: "Deep feature response curve for learned descriptor matching.",
      ),
      CapabilityItemModel(
        name: "Deep Attention Correspondence Pruning",
        status: "Roadmap",
        category: "Deep Models",
        notes: "Deep transformer correspondence pruning for future releases.",
      ),
      CapabilityItemModel(
        name: "Parallax-Aware Sub-Pixel Optimizer",
        status: "Roadmap",
        category: "Optimization",
        notes: "Sub-pixel correlation refinement for future releases.",
      ),
    ];
  }
}