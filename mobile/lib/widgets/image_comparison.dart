import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../services/api_service.dart';

enum ComparisonMode { reference, registered, overlay, difference }

class ImageComparisonViewer extends StatefulWidget {
  final Widget referenceWidget;
  final String? registeredUrl;
  final String? overlayUrl;
  final String? differenceUrl;

  const ImageComparisonViewer({
    super.key,
    required this.referenceWidget,
    this.registeredUrl,
    this.overlayUrl,
    this.differenceUrl,
  });

  @override
  State<ImageComparisonViewer> createState() => _ImageComparisonViewerState();
}

class _ImageComparisonViewerState extends State<ImageComparisonViewer> {
  ComparisonMode _mode = ComparisonMode.registered;
  double _overlayAlpha = 0.5;
  final TransformationController _transformController = TransformationController();

  void _resetZoom() {
    _transformController.value = Matrix4.identity();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Responsive Control Bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: LunarTheme.surfaceCard,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(10)),
            border: Border.all(color: LunarTheme.border),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Mode Toggles inside Expanded with Wrap
              Expanded(
                child: Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    _buildTabButton("REF", ComparisonMode.reference),
                    _buildTabButton("REGISTERED", ComparisonMode.registered),
                    _buildTabButton("OVERLAY", ComparisonMode.overlay),
                    _buildTabButton("DIFF", ComparisonMode.difference),
                  ],
                ),
              ),
              const SizedBox(width: 6),
              // Zoom Reset
              IconButton(
                icon: const Icon(Icons.fit_screen, size: 16, color: Colors.white),
                tooltip: "Reset Zoom",
                onPressed: _resetZoom,
                constraints: const BoxConstraints(),
                padding: const EdgeInsets.all(6),
              ),
            ],
          ),
        ),

        // Main Viewer Canvas with InteractiveViewer
        Container(
          height: 320,
          decoration: BoxDecoration(
            color: LunarTheme.background,
            borderRadius: const BorderRadius.vertical(bottom: Radius.circular(10)),
            border: Border.all(color: LunarTheme.border),
          ),
          clipBehavior: Clip.antiAlias,
          child: Stack(
            fit: StackFit.expand,
            children: [
              InteractiveViewer(
                transformationController: _transformController,
                minScale: 0.8,
                maxScale: 6.0,
                child: Center(
                  child: _buildActiveImage(),
                ),
              ),

              // Current Mode Overlay Label
              Positioned(
                top: 8,
                left: 8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.75),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: LunarTheme.borderLight),
                  ),
                  child: Text(
                    _mode.name.toUpperCase(),
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Alpha Slider when Overlay Mode is active
        if (_mode == ComparisonMode.overlay) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: LunarTheme.surfaceCard,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: LunarTheme.border),
            ),
            child: Row(
              children: [
                const Text(
                  "REF (0%)",
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: LunarTheme.textSecondary),
                ),
                Expanded(
                  child: Slider(
                    value: _overlayAlpha,
                    min: 0.0,
                    max: 1.0,
                    activeColor: Colors.white,
                    inactiveColor: LunarTheme.border,
                    thumbColor: Colors.white,
                    onChanged: (val) {
                      setState(() => _overlayAlpha = val);
                    },
                  ),
                ),
                const Text(
                  "MOV (100%)",
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: LunarTheme.textSecondary),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildTabButton(String label, ComparisonMode targetMode) {
    final isSelected = _mode == targetMode;
    return InkWell(
      onTap: () => setState(() => _mode = targetMode),
      borderRadius: BorderRadius.circular(4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : LunarTheme.surfaceElevated,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: isSelected ? Colors.white : LunarTheme.border,
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.5,
            color: isSelected ? Colors.black : LunarTheme.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildActiveImage() {
    switch (_mode) {
      case ComparisonMode.reference:
        return widget.referenceWidget;
      case ComparisonMode.registered:
        return _renderImageFromSource(widget.registeredUrl);
      case ComparisonMode.overlay:
        // Blended Stack based on _overlayAlpha
        return Stack(
          alignment: Alignment.center,
          children: [
            widget.referenceWidget,
            Opacity(
              opacity: _overlayAlpha,
              child: _renderImageFromSource(widget.registeredUrl),
            ),
          ],
        );
      case ComparisonMode.difference:
        return _renderImageFromSource(widget.differenceUrl);
    }
  }

  Widget _renderImageFromSource(String? urlOrAsset) {
    if (urlOrAsset == null || urlOrAsset.isEmpty) {
      return const Center(
        child: Text("No artifact generated for this mode", style: TextStyle(color: LunarTheme.textTertiary)),
      );
    }

    if (urlOrAsset.startsWith("assets/")) {
      return Image.asset(urlOrAsset, fit: BoxFit.contain);
    }

    final fullUrl = apiService.resolveFullUrl(urlOrAsset);
    return Image.network(
      fullUrl,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) => const Center(
        child: Text("Artifact loading failed", style: TextStyle(color: LunarTheme.textTertiary, fontSize: 12)),
      ),
      loadingBuilder: (_, child, progress) {
        if (progress == null) return child;
        return const Center(child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white));
      },
    );
  }
}
