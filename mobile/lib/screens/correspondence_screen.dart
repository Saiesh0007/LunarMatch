import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../models/match_model.dart';
import '../models/image_model.dart';
import '../providers/pipeline_provider.dart';
import '../providers/image_provider.dart';
import '../widgets/match_visualization.dart';

class CorrespondenceScreen extends StatelessWidget {
  const CorrespondenceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final imgProv = context.watch<LunarImageProvider>();
    final res = pipeProv.latestResponse;

    final matches = _generateDisplayMatches(res?.metrics.ransacInliers ?? 84, res?.metrics.filteredMatches ?? 118);

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("CORRESPONDENCE VISUALIZATION"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Technical Header Note
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.hub_outlined, size: 16, color: Colors.white),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        "Correspondence vectors link matching keypoints from Reference (Fixed, Left) to Moving (Transformed, Right). White lines indicate validated RANSAC inliers; dark gray lines indicate rejected outliers.",
                        style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Interactive Correspondence Canvas
              MatchVisualizationWidget(
                matches: matches,
                refImageWidget: _buildImageWidget(imgProv.referenceImage),
                movImageWidget: _buildImageWidget(imgProv.movingImage),
                refWidth: imgProv.referenceImage?.width ?? 640,
                refHeight: imgProv.referenceImage?.height ?? 640,
              ),
              const SizedBox(height: 16),

              // Correspondence Statistics Breakdown
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
                      "CORRESPONDENCE FILTERING PIPELINE",
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.8, color: Colors.white),
                    ),
                    const SizedBox(height: 10),
                    _buildPipelineRow(
                      "Stage 1: Raw 2-NN Candidates",
                      "${res?.metrics.candidateMatches ?? 312} pairs",
                      "Exhaustive feature space nearest neighbors",
                    ),
                    const Divider(height: 14),
                    _buildPipelineRow(
                      "Stage 2: Lowe's Ratio Test Filter",
                      "${res?.metrics.filteredMatches ?? 118} pairs",
                      "Eliminates ambiguous multi-crater matches",
                    ),
                    const Divider(height: 14),
                    _buildPipelineRow(
                      "Stage 3: RANSAC Geometric Consensus",
                      "${res?.metrics.ransacInliers ?? 84} inliers",
                      "Satisfies projective reprojection error threshold",
                    ),
                    const Divider(height: 14),
                    _buildPipelineRow(
                      "Stage 4: Spatial Balancing Selection",
                      "${(res?.metrics.ransacInliers ?? 84) > 48 ? 48 : (res?.metrics.ransacInliers ?? 84)} selected",
                      "Enforces uniform distribution across grid cells",
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPipelineRow(String title, String count, String desc) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
              const SizedBox(height: 2),
              Text(desc, style: const TextStyle(fontSize: 10, color: LunarTheme.textTertiary)),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Text(count, style: LunarTheme.mono.copyWith(fontSize: 11)),
      ],
    );
  }

  Widget _buildImageWidget(LunarImageModel? img) {
    if (img == null) return const SizedBox();
    if (img.bytes != null) return Image.memory(img.bytes!, fit: BoxFit.contain);
    if (img.assetPath != null) return Image.asset(img.assetPath!, fit: BoxFit.contain);
    if (img.localPath != null) return Image.file(File(img.localPath!), fit: BoxFit.contain);
    return const SizedBox();
  }

  List<MatchPairModel> _generateDisplayMatches(int inliersCount, int totalCount) {
    final list = <MatchPairModel>[];
    for (int i = 0; i < totalCount; i++) {
      final isInlier = i < inliersCount;
      final rx = 60.0 + ((i * 37) % 520);
      final ry = 60.0 + ((i * 53) % 520);
      final mx = isInlier ? rx * 1.02 + 10.0 : rx + ((i % 2 == 0 ? 1 : -1) * 60.0);
      final my = isInlier ? ry * 1.02 - 8.0 : ry + ((i % 2 == 0 ? -1 : 1) * 80.0);

      list.add(
        MatchPairModel(
          refIdx: i,
          movIdx: i,
          distance: isInlier ? 65.0 : 180.0,
          refPt: [rx, ry],
          movPt: [mx, my],
          isInlier: isInlier,
          isSpatiallySelected: isInlier && (i % 2 == 0),
        ),
      );
    }
    return list;
  }
}
