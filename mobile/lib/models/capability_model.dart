class CapabilityItemModel {
  final String name;
  final String category;
   final String status; // "VERIFIED", "DEMO", "RESEARCH_ROADMAP"
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
       status: json['status'] ?? 'VERIFIED',
       verified: json['verified'] ?? true,
       notes: json['notes'] ?? '',
     );
  }
}
