import 'dart:typed_data';

class LunarImageModel {
  final String id;
  final String name;
  final String? localPath;
  final String? assetPath;
  final String? networkUrl;
  final Uint8List? bytes;
  final int width;
  final int height;
  final String sensor;
  final bool isAsset;

  const LunarImageModel({
    required this.id,
    required this.name,
    this.localPath,
    this.assetPath,
    this.networkUrl,
    this.bytes,
    required this.width,
    required this.height,
    required this.sensor,
    this.isAsset = false,
  });

  LunarImageModel copyWith({
    String? id,
    String? name,
    String? localPath,
    String? assetPath,
    String? networkUrl,
    Uint8List? bytes,
    int? width,
    int? height,
    String? sensor,
    bool? isAsset,
  }) {
    return LunarImageModel(
      id: id ?? this.id,
      name: name ?? this.name,
      localPath: localPath ?? this.localPath,
      assetPath: assetPath ?? this.assetPath,
      networkUrl: networkUrl ?? this.networkUrl,
      bytes: bytes ?? this.bytes,
      width: width ?? this.width,
      height: height ?? this.height,
      sensor: sensor ?? this.sensor,
      isAsset: isAsset ?? this.isAsset,
    );
  }
}

class DemoPairModel {
  final String pairId;
  final String name;
  final String description;
  final String referenceImageId;
  final String movingImageId;
  final String referenceSensor;
  final String movingSensor;
  final String referenceAssetPath;
  final String movingAssetPath;
  final String provenanceNote;

  const DemoPairModel({
    required this.pairId,
    required this.name,
    required this.description,
    required this.referenceImageId,
    required this.movingImageId,
    required this.referenceSensor,
    required this.movingSensor,
    required this.referenceAssetPath,
    required this.movingAssetPath,
    required this.provenanceNote,
  });

  factory DemoPairModel.fromJson(Map<String, dynamic> json) {
    return DemoPairModel(
      pairId: json['pair_id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      referenceImageId: json['reference_image_id'] ?? '',
      movingImageId: json['moving_image_id'] ?? '',
      referenceSensor: json['reference_sensor'] ?? 'OHRC',
      movingSensor: json['moving_sensor'] ?? 'TMC-2',
      referenceAssetPath: 'assets/demo/pair_${json['pair_id'] == 'pair_b' ? 'b' : 'a'}_ref.png',
      movingAssetPath: 'assets/demo/pair_${json['pair_id'] == 'pair_b' ? 'b' : 'a'}_mov.png',
      provenanceNote: json['provenance_note'] ?? 'SYNTHETIC PROTOTYPE',
    );
  }
}
