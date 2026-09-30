class CapabilityItemModel {
  final String name;
  final String category;
  final String status;
  final bool verified;
  final String notes;

  const CapabilityItemModel({
    required this.name,
    this.category = '',
    this.status = 'Operational',
    this.verified = true,
    this.notes = '',
  });

  factory CapabilityItemModel.fromJson(Map<String, dynamic> json) {
    return CapabilityItemModel(
      name: json['name'] ?? '',
      category: json['category'] ?? '',
      status: json['status'] ?? 'Operational',
      verified: json['verified'] ?? false,
      notes: json['notes'] ?? '',
    );
  }
}
