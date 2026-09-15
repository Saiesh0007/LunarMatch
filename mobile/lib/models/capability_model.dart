class CapabilityItemModel {
  final String name;
  final String category;
  final String status;
  final String notes;

  const CapabilityItemModel({
    required this.name,
    required this.category,
    required this.status,
    required this.notes,
  });

  factory CapabilityItemModel.fromJson(Map<String, dynamic> json) {
    return CapabilityItemModel(
      name: json['name'] ?? '',
      category: json['category'] ?? '',
      status: json['status'] ?? 'Active',
      notes: json['notes'] ?? '',
    );
  }
}