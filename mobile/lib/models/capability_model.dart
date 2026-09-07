class CapabilityItemModel {
  final String name;
  final String category;
  final String status; // "IMPLEMENTED", "SIMULATED", "PLANNED"
  final bool verified;
  final String notes;

  const CapabilityItemModel({
    required this.name,
    required this.category,
    required this.status,
    required this.verified,
    required this.notes,
  });

  factory CapabilityItemModel.fromJson(Map<String, dynamic> json) {
    return CapabilityItemModel(
      name: json['name'] ?? '',
      category: json['category'] ?? '',
      status: json['status'] ?? 'PLANNED',
      verified: json['verified'] ?? false,
      notes: json['notes'] ?? '',
    );
  }
}
