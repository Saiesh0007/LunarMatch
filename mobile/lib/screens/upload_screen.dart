import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/image_model.dart';
import '../providers/image_provider.dart';
import '../services/image_service.dart';
import '../widgets/lunar_image_card.dart';
import '../utils/animation_utils.dart';

class UploadScreen extends StatelessWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final imgProv = context.watch<LunarImageProvider>();
    final animTarget = AnimationUtils.targetFor(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text("SELECT LUNAR IMAGES"),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline, size: 20, color: Colors.white),
            tooltip: "Clear Images",
            onPressed: imgProv.clearImages,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Technical Instructions & Terminology banner
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, size: 16, color: Colors.white),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        "REFERENCE is the fixed coordinate frame. MOVING is the image that gets transformed. Both must share overlapping surface features.",
                        style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.35),
                      ),
                    ),
                  ],
                ),
              )
                  .animate(target: animTarget)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 16),

              // Reference Image Card
              LunarImageCard(
                roleTitle: "REFERENCE IMAGE",
                roleSubtitle: "Fixed coordinate system (Reference Frame)",
                image: imgProv.referenceImage,
                currentSensor: imgProv.referenceSensor,
                roleColor: Colors.white,
                onSensorChanged: (s) => imgProv.setReferenceSensor(s),
                onUploadPressed: () async {
                  final img = await ImagePickerService.pickImage(sensor: imgProv.referenceSensor);
                  if (img != null) imgProv.setReferenceImage(img);
                },
                onDemoPressed: () async {
                  final img = await ImagePickerService.loadBundledDemoImage(
                    assetPath: "assets/demo/pair_a_ref.png",
                    imageId: "demo_pair_a_ref",
                    name: "Pair A Reference (OHRC)",
                    sensor: "OHRC",
                  );
                  imgProv.setReferenceImage(img);
                },
              )
                  .animate(target: animTarget)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 12),

              // Swap Button
              Center(
                child: OutlinedButton.icon(
                  onPressed: imgProv.hasBothImages ? imgProv.swapImages : null,
                  icon: const Icon(Icons.swap_vert, size: 16),
                  label: const Text("SWAP REFERENCE & MOVING"),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    foregroundColor: Colors.white,
                    side: const BorderSide(color: LunarTheme.borderLight),
                  ),
                ),
              )
                  .animate(target: animTarget, delay: 50.ms)
                  .fadeIn(duration: 250.ms),
              const SizedBox(height: 12),

              // Moving Image Card
              LunarImageCard(
                roleTitle: "MOVING IMAGE",
                roleSubtitle: "Image to transform (Warped Coordinate Frame)",
                image: imgProv.movingImage,
                currentSensor: imgProv.movingSensor,
                roleColor: Colors.white,
                onSensorChanged: (s) => imgProv.setMovingSensor(s),
                onUploadPressed: () async {
                  final img = await ImagePickerService.pickImage(sensor: imgProv.movingSensor);
                  if (img != null) imgProv.setMovingImage(img);
                },
                onDemoPressed: () async {
                  final img = await ImagePickerService.loadBundledDemoImage(
                    assetPath: "assets/demo/pair_a_mov.png",
                    imageId: "demo_pair_a_mov",
                    name: "Pair A Moving (TMC-2)",
                    sensor: "TMC-2",
                  );
                  imgProv.setMovingImage(img);
                },
              )
                  .animate(target: animTarget, delay: 100.ms)
                  .fadeIn(duration: 300.ms, curve: Curves.easeOut)
                  .slideY(begin: 0.1, end: 0, duration: 300.ms, curve: Curves.easeOut),
              const SizedBox(height: 20),

              // Demo Pairs Quick Load
              const Text(
                "IMAGE PAIRS",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: LunarTheme.textTertiary,
                ),
              ),
              const SizedBox(height: 8),

              _buildDemoPairSelector(
                context: context,
                pairId: "pair_a",
                title: "PAIR A — LUNAR SURFACE",
                sensors: "OHRC Optical ↔ TMC-2 Stereo",
                provenance: "Surface alignment across multi-sensor impact crater terrain.",
                onSelect: () {
                  final pair = DemoPairModel(
                    pairId: "pair_a",
                    name: "Pair A — Lunar Surface",
                    description: "OHRC Optical vs TMC-2 Stereo alignment over impact crater basin.",
                    referenceImageId: "demo_pair_a_ref",
                    movingImageId: "demo_pair_a_mov",
                    referenceSensor: "OHRC",
                    movingSensor: "TMC-2",
                    referenceAssetPath: "assets/demo/pair_a_ref.png",
                    movingAssetPath: "assets/demo/pair_a_mov.png",
                    provenanceNote: "Surface alignment across multi-sensor impact crater terrain.",
                  );
                  imgProv.loadDemoPair(pair);
                },
              ),
              const SizedBox(height: 8),

              _buildDemoPairSelector(
                context: context,
                pairId: "pair_b",
                title: "PAIR B — STEEP ILLUMINATION DELTA",
                sensors: "LRO NAC ↔ IIRS Hyperspectral (60° Sun Angle Delta)",
                provenance: "Cross-modality alignment under 60° solar illumination variation.",
                onSelect: () {
                  final pair = DemoPairModel(
                    pairId: "pair_b",
                    name: "Pair B — High Illumination Delta",
                    description: "LRO NAC vs IIRS Hyperspectral alignment with steep 60° solar illumination delta.",
                    referenceImageId: "demo_pair_b_ref",
                    movingImageId: "demo_pair_b_mov",
                    referenceSensor: "LRO NAC",
                    movingSensor: "IIRS",
                    referenceAssetPath: "assets/demo/pair_b_ref.png",
                    movingAssetPath: "assets/demo/pair_b_mov.png",
                    provenanceNote: "Cross-modality alignment under 60° solar illumination variation.",
                  );
                  imgProv.loadDemoPair(pair);
                },
              ),
              const SizedBox(height: 24),

              // Next Button
              ElevatedButton.icon(
                onPressed: imgProv.hasBothImages
                    ? () => Navigator.pushNamed(context, AppRoutes.configure)
                    : null,
                icon: const Icon(Icons.tune_outlined, size: 18),
                label: const Text("CONFIGURE PIPELINE"),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black,
                  disabledBackgroundColor: const Color(0xFF222222),
                  disabledForegroundColor: const Color(0xFF555555),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDemoPairSelector({
    required BuildContext context,
    required String pairId,
    required String title,
    required String sensors,
    required String provenance,
    required VoidCallback onSelect,
  }) {
    final imgProv = context.watch<LunarImageProvider>();
    final isSelected = imgProv.selectedDemoPair?.pairId == pairId;

    return Container(
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isSelected ? Colors.white : LunarTheme.border,
          width: isSelected ? 1.2 : 1.0,
        ),
      ),
      child: InkWell(
        onTap: onSelect,
        borderRadius: BorderRadius.circular(10),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  if (isSelected) ...[
                    const SizedBox(width: 8),
                    const Icon(Icons.check_circle, size: 16, color: Colors.white),
                  ],
                ],
              ),
              const SizedBox(height: 4),
              Text(
                sensors,
                style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
              ),

            ],
          ),
        ),
      ),
    );
  }
}
