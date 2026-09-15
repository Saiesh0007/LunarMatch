class CapabilityItemModel {
  final String name;
  final String? category;
  final String? description;
  final String? notes;
  final bool active;

  const CapabilityItemModel({
    required this.name,
    this.category,
    this.description,
    this.notes,
    this.active = true,
  });

  factory CapabilityItemModel.fromJson(Map<String, dynamic> json) {
    return CapabilityItemModel(
      name: (json['name'] ?? '') as String,
      category: json['category'] as String?,
      description: json['description'] as String?,
      notes: json['notes'] as String?,
      active: (json['active'] as bool?) ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      if (category != null) 'category': category,
      if (description != null) 'description': description,
      if (notes != null) 'notes': notes,
      'active': active,
    };
  }
}
