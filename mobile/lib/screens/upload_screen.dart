import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../models/image_model.dart';
import '../providers/image_provider.dart';
import '../services/image_service.dart';

class UploadScreen extends StatelessWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final imgProv = context.watch<LunarImageProvider>();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("New Registration"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Upload zone: Source Image
              _buildUploadZone(
                title: "Source Image",
                subtitle: "Primary image to register",
                image: imgProv.referenceImage,
                onUpload: () async {
                  final picked = await ImagePickerService.pickImage(sensor: imgProv.referenceSensor);
                  if (picked != null) imgProv.setReferenceImage(picked);
                },
              ),
              const SizedBox(height: 16),

              // Upload zone: Reference Image
              _buildUploadZone(
                title: "Reference Image",
                subtitle: "Reference coordinate frame",
                image: imgProv.movingImage,
                onUpload: () async {
                  final picked = await ImagePickerService.pickImage(sensor: imgProv.movingSensor);
                  if (picked != null) imgProv.setMovingImage(picked);
                },
              ),
              const SizedBox(height: 16),

              // Upload zone: DEM Optional
              _buildUploadZone(
                title: "DEM (Optional)",
                subtitle: "Digital elevation model for terrain correction",
                image: null,
                onUpload: () async {
                  final picked = await ImagePickerService.pickImage(sensor: "DEM");
                  // Handle DEM upload if needed
                },
              ),
              const SizedBox(height: 16),

              // Supported formats caption
              Center(
                child: Text(
                  "Supported formats: .png · .jpg · .tif (≤ 100 MB)",
                  style: LunarTheme.mono.copyWith(
                    fontSize: 11,
                    color: LunarTheme.textTertiary,
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Continue button
              ElevatedButton(
                onPressed: imgProv.hasBothImages
                    ? () => Navigator.pushNamed(context, AppRoutes.configure)
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: LunarTheme.primary,
                  foregroundColor: Colors.black,
                  disabledBackgroundColor: LunarTheme.surfaceElevated,
                  disabledForegroundColor: LunarTheme.textTertiary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  textStyle: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                child: const Text("Continue"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUploadZone({
    required String title,
    required String subtitle,
    required LunarImageModel? image,
    required VoidCallback onUpload,
  }) {
    final hasImage = image != null;

    return Container(
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: hasImage ? LunarTheme.success : LunarTheme.border,
          width: 1,
          style: BorderStyle.solid,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: LunarTheme.surfaceElevated,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
              border: Border(
                bottom: BorderSide(color: LunarTheme.border, width: 1),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: LunarTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: LunarTheme.mono.copyWith(
                    fontSize: 10,
                    color: LunarTheme.textTertiary,
                  ),
                ),
              ],
            ),
          ),

          // Content area
          Padding(
            padding: const EdgeInsets.all(16),
            child: hasImage
                ? Column(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: image.localPath != null
                            ? Image.file(
                                File(image.localPath!),
                                height: 160,
                                width: double.infinity,
                                fit: BoxFit.cover,
                              )
                            : image.bytes != null
                                ? Image.memory(
                                    image.bytes!,
                                    height: 160,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                  )
                                : const SizedBox(
                                    height: 160,
                                    child: Center(child: Text("No image loaded")),
                                  ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              image.name,
                              style: LunarTheme.mono.copyWith(
                                fontSize: 11,
                                color: LunarTheme.textSecondary,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          TextButton.icon(
                            onPressed: onUpload,
                            icon: const Icon(Icons.refresh, size: 14),
                            label: const Text("Replace"),
                            style: TextButton.styleFrom(
                              foregroundColor: LunarTheme.primary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  )
                : InkWell(
                    onTap: onUpload,
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      height: 120,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: LunarTheme.border,
                          width: 1,
                          style: BorderStyle.solid,
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.cloud_upload_outlined,
                            size: 32,
                            color: LunarTheme.textTertiary,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            "Tap to select image",
                            style: LunarTheme.mono.copyWith(
                              fontSize: 11,
                              color: LunarTheme.textTertiary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}