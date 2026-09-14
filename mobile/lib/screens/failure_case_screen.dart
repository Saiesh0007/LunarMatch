import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../services/api_service.dart';

class FailureCaseScreen extends StatefulWidget {
  final ApiService? apiClient;
  const FailureCaseScreen({super.key, this.apiClient});

  @override
  State<FailureCaseScreen> createState() => _FailureCaseScreenState();
}

class _FailureCaseScreenState extends State<FailureCaseScreen> {
  bool _loading = true;
  Map<String, dynamic>? _failureData;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadFailureCase();
  }

  Future<void> _loadFailureCase() async {
    final api = widget.apiClient ?? apiService;
    try {
      setState(() {
        _loading = true;
        _failureData = null;
        _error = null;
      });
      final res = await api.fetchFailureCase();
      setState(() {
        _failureData = res;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = "Error: $e";
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("Failure Detection"),
        automaticallyImplyLeading: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: LunarTheme.borderFocus),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "When LunarMatch Says NO",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.8,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Honest rejection beats fabricated confidence. We return REGISTRATION_NOT_RELIABLE instead of a wrong transform.",
                      style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Image pair placeholder
              _buildImagePair(),
              const SizedBox(height: 16),

              // Loading state
              if (_loading) ...[
                Center(
                  child: Column(
                    children: [
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      ),
                      const SizedBox(height: 12),
                      const Text("Loading failure case\u2026", style: TextStyle(color: LunarTheme.textSecondary)),
                    ],
                  ),
                ),
              ]

              // Error state
              else if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Error: $_error", style: const TextStyle(color: Colors.white)),
                      const SizedBox(height: 8),
                      ElevatedButton(onPressed: _loadFailureCase, child: const Text("RETRY")),
                    ],
                  ),
                ),
              ]

              // Results
              else if (_failureData != null) ...[
                _buildChecklist(),
                const SizedBox(height: 16),
                _buildReasonCard(),
                const SizedBox(height: 16),
                _buildNarrative(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImagePair() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "REJECTED PAIR — Match attempts shown",
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
          ),
          const SizedBox(height: 8),
          Container(
            height: 200,
            decoration: BoxDecoration(
              color: const Color(0xFF050505),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Center(
              child: Text(
                "Reference [left] + Moving [right]\nOutliers shown in red\n(In production: matched keypoint overlay)",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 11, color: LunarTheme.textTertiary, height: 1.5),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChecklist() {
    final criteria = _failureData?['criteria'] as List<dynamic>? ?? [];

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "ACCEPTANCE CRITERIA",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.0,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 12),
          ...criteria.map<Widget>((c) {
            final pass = c['pass'] as bool;
            final label = c['label'] as String;
            final value = c['display'] as String;
            final threshold = c['threshold'];
            final thresholdStr = threshold is List
                ? "[${threshold[0]}, ${threshold[1]}]"
                : "<= $threshold";
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Icon(
                    pass ? Icons.check_circle_outline : Icons.cancel,
                    size: 16,
                    color: pass ? Colors.white : LunarTheme.borderFocus,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      label,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: pass ? Colors.white : LunarTheme.textSecondary,
                      ),
                    ),
                  ),
                  Text(
                    value,
                    style: LunarTheme.mono.copyWith(fontSize: 11),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: pass ? Colors.white : LunarTheme.borderFocus,
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: Text(
                      pass ? "PASS" : "FAIL",
                      style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w900,
                        color: pass ? Colors.black : Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  SizedBox(
                    width: 50,
                    child: Text(
                      thresholdStr,
                      style: TextStyle(fontSize: 9, color: LunarTheme.textTertiary),
                      textAlign: TextAlign.right,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildReasonCard() {
    final decision = _failureData?['decision'] as String? ?? 'REGISTRATION_NOT_RELIABLE';
    final failed = _failureData?['failed_criteria'] as List<dynamic>? ?? [];
    final failedStr = failed.isNotEmpty ? failed.join(', ') : 'unknown';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceElevated,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.borderFocus),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            decision,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w900,
              letterSpacing: 0.8,
              color: LunarTheme.borderFocus,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            "$decision — ${failed.length} criteria failed: $failedStr",
            style: const TextStyle(fontSize: 11, color: Colors.white),
          ),
        ],
      ),
    );
  }

  Widget _buildNarrative() {
    final note = _failureData?['note'] as String? ?? '';
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "WHY THIS MATTERS",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.0,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            note.isNotEmpty ? note : "We return NOT_RELIABLE rather than a wrong transform. Downstream users can trust the metric.",
            style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary, height: 1.5),
          ),
        ],
      ),
    );
  }
}
