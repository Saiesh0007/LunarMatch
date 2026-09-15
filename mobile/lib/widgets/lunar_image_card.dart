import 'dart:io';
import 'package:flutter/material.dart';
import '../models/image_model.dart';
import '../app/theme.dart';
import '../utils/constants.dart';

class LunarImageCard extends StatelessWidget {
  final String roleTitle; // "REFERENCE IMAGE" or "MOVING IMAGE"
  final String roleSubtitle; // "Fixed coordinate system" or "Image to transform"
  final LunarImageModel? image;
  final String currentSensor;
  final ValueChanged<String> onSensorChanged;
  final VoidCallback onUploadPressed;
  final VoidCallback? onDemoPressed;
  final Color roleColor;

  const LunarImageCard({
    super.key,
    required this.roleTitle,
    required this.roleSubtitle,
    required this.image,
    required this.currentSensor,
    required this.onSensorChanged,
    required this.onUploadPressed,
    this.onDemoPressed,
    this.roleColor = Colors.white,
  });

  @override
  Widget build(BuildContext context) {
    final hasImage = image != null;

    return Container(
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: hasImage ? Colors.white : LunarTheme.border,
          width: hasImage ? 1.2 : 1.0,
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Responsive Header: Stacks gracefully on narrow screens (< 350px)
          LayoutBuilder(
            builder: (context, constraints) {
              final isVeryNarrow = constraints.maxWidth < 280;

              final titleContent = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 7,
                        height: 7,
                        decoration: BoxDecoration(
                          color: hasImage ? Colors.white : LunarTheme.textTertiary,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          roleTitle,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    roleSubtitle,
                    style: const TextStyle(fontSize: 11, color: LunarTheme.textTertiary),
                  ),
                ],
              );

              final dropdownWidget = Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: LunarTheme.borderLight),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: currentSensor,
                    isDense: true,
                    dropdownColor: LunarTheme.surfaceElevated,
                    icon: const Icon(Icons.arrow_drop_down, color: Colors.white, size: 18),
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                    items: AppConstants.sensorList.map((s) {
                      return DropdownMenuItem<String>(
                        value: s,
                        child: Text(s),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) onSensorChanged(val);
                    },
                  ),
                ),
              );

              if (isVeryNarrow) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    titleContent,
                    const SizedBox(height: 8),
                    dropdownWidget,
                  ],
                );
              }

              return Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(child: titleContent),
                  const SizedBox(width: 8),
                  Flexible(child: dropdownWidget),
                ],
              );
            },
          ),
          const SizedBox(height: 12),

          // Responsive Preview area
          Container(
            height: 170,
            width: double.infinity,
            decoration: BoxDecoration(
              color: LunarTheme.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: LunarTheme.border),
            ),
            clipBehavior: Clip.antiAlias,
            child: image == null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.satellite_alt_outlined,
                          size: 36,
                          color: LunarTheme.textTertiary,
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "No lunar image selected",
                          style: TextStyle(fontSize: 12, color: LunarTheme.textTertiary),
                        ),
                      ],
                    ),
                  )
                : _buildImageWidget(image!),
          ),
          const SizedBox(height: 12),

          // Metadata row if image loaded
          if (image != null) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    image!.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: LunarTheme.textSecondary),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  "${image!.width} × ${image!.height} px",
                  style: LunarTheme.mono.copyWith(fontSize: 11, color: LunarTheme.textSecondary),
                ),
              ],
            ),
            const SizedBox(height: 10),
          ],

          // Buttons Row
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: onUploadPressed,
              icon: const Icon(Icons.file_upload_outlined, size: 15),
              label: Text(image == null ? "Upload Image" : "Replace"),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 11, horizontal: 8),
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImageWidget(LunarImageModel img) {
    if (img.bytes != null) {
      return Image.memory(img.bytes!, fit: BoxFit.cover);
    }
    if (img.assetPath != null) {
      return Image.asset(img.assetPath!, fit: BoxFit.cover);
    }
    if (img.localPath != null) {
      return Image.file(File(img.localPath!), fit: BoxFit.cover);
    }
    return const Center(child: Text("Failed to load image"));
  }
}
