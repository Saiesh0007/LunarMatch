class MatchPairModel {
  final int refIdx;
  final int movIdx;
  final double distance;
  final List<double> refPt;
  final List<double> movPt;
  final bool isInlier;
  final bool isSpatiallySelected;

  const MatchPairModel({
    required this.refIdx,
    required this.movIdx,
    required this.distance,
    required this.refPt,
    required this.movPt,
    this.isInlier = false,
    this.isSpatiallySelected = false,
  });

  factory MatchPairModel.fromJson(Map<String, dynamic> json) {
    return MatchPairModel(
      refIdx: json['ref_idx'] ?? 0,
      movIdx: json['mov_idx'] ?? 0,
      distance: (json['distance'] as num?)?.toDouble() ?? 0.0,
      refPt: ((json['ref_pt'] as List<dynamic>?) ?? [0.0, 0.0])
          .map((e) => (e as num).toDouble())
          .toList(),
      movPt: ((json['mov_pt'] as List<dynamic>?) ?? [0.0, 0.0])
          .map((e) => (e as num).toDouble())
          .toList(),
      isInlier: json['is_inlier'] ?? false,
      isSpatiallySelected: json['is_spatially_selected'] ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'ref_idx': refIdx,
    'mov_idx': movIdx,
    'distance': distance,
    'ref_pt': refPt,
    'mov_pt': movPt,
    'is_inlier': isInlier,
    'is_spatially_selected': isSpatiallySelected,
  };
}
