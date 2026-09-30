import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/services.dart';
import '../models/image_model.dart';
import 'api_service.dart';

class ImagePickerService {
  static Future<LunarImageModel?> pickImage({required String sensor}) async {
    final files = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'],
      withData: true,
    );

    if (files.isEmpty) return null;

    final file = files.first;
    Uint8List? bytes;
    try {
      bytes = await file.readAsBytes();
    } catch (_) {
      if (file.path != null) {
        try {
          bytes = await File(file.path!).readAsBytes();
        } catch (_) {}
      }
    }

    final path = file.path;
    if (bytes == null && path == null) return null;

    // Default dimensions before upload/decode
    int w = 1024;
    int h = 1024;
    String id = file.name;

    // If online, upload to FastAPI backend to register image_id and real dimensions
    try {
      if (bytes != null) {
        final uploadRes = await apiService.uploadImageBytes(bytes, file.name);
        id = uploadRes['image_id'] ?? file.name;
        w = uploadRes['width'] ?? 1024;
        h = uploadRes['height'] ?? 1024;
      }
    } catch (_) {
      // Local fallback ID
      id = file.name;
    }

    return LunarImageModel(
      id: id,
      name: file.name,
      localPath: path,
      bytes: bytes,
      width: w,
      height: h,
      sensor: sensor,
      isAsset: false,
    );
  }

  static Future<LunarImageModel> loadBundledDemoImage({
    required String assetPath,
    required String imageId,
    required String name,
    required String sensor,
  }) async {
    final byteData = await rootBundle.load(assetPath);
    final bytes = byteData.buffer.asUint8List();

    return LunarImageModel(
      id: imageId,
      name: name,
      assetPath: assetPath,
      bytes: bytes,
      width: 640,
      height: 640,
      sensor: sensor,
      isAsset: true,
    );
  }
}
