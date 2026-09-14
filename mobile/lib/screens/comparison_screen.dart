import 'package:flutter/material.dart';
import '../app/theme.dart';
import '../services/api_service.dart';
import '../utils/formatters.dart';
import '../widgets/metric_card.dart';

class ComparisonScreen extends StatefulWidget {
  final ApiService? apiClient;
  const ComparisonScreen({super.key, this.apiClient});

  @override
  State<ComparisonScreen> createState() => _ComparisonScreenState();
}

class _ComparisonScreenState extends State<ComparisonScreen> {
  late final ApiService _api;
  bool _loadingSift = true;
  bool _loadingLunar = true;
  Map<String, dynamic>? _comparisonData;
  String? _error;

  @override
  void initState() {
    super.initState();
    _api = widget.apiClient ?? ApiService();
    _loadComparison();
  }

  Future<void> _loadComparison() async {
    try {
      setState(() {
        _loadingSift = true;
        _loadingLunar = true;
        _comparisonData = null;
        _error = null;
      });
      final res = await _api.fetchDemoCompare(
        "Pair A: bundled prototype",
      );
      setState(() {
        _comparisonData = res;
        _loadingSift = false;
        _loadingLunar = false;
      });
    } catch (e) {
      setState(() {
        _error = "Comparison error: $e";
        _loadingSift = false;
        _loadingLunar = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final data = _comparisonData;

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        title: const Text("SIFT vs LunarMatch"),
        automaticallyImplyLeading: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Container(
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
                      "SIFT vs LunarMatch — Same Input Pair",
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.6,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      data != null ? data['pair_name'] ?? 'Pair A: bundled prototype' : 'Pair A: bundled prototype',
                      style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Loading state
              if (_loadingSift || _loadingLunar) ...[
                _buildLoadingCard("Running SIFT baseline\u2026", Icons.cached_outlined),
                const SizedBox(height: 12),
                _buildLoadingCard("Running LunarMatch\u2026", Icons.cached_outlined),
                const SizedBox(height: 12),
                _buildLoadingCard("Computing deltas\u2026", Icons.cached_outlined),
              ]

              // Error state
              else if (_error != null) ...[
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
                      Text("Error: $_error", style: const TextStyle(color: Colors.white, fontSize: 12)),
                      const SizedBox(height: 8),
                      ElevatedButton(
                        onPressed: _loadComparison,
                        child: const Text("RETRY"),
                      ),
                    ],
                  ),
                ),
              ]

              // Results
              else ...[
                // Two-column comparison
                LayoutBuilder(
                  builder: (context, constraints) {
                    final isWide = constraints.maxWidth > 700;
                    if (isWide) {
                      return Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(child: _buildPipelineCard("SIFT BASELINE", _comparisonData?['sift'], false)),
                          const SizedBox(width: 12),
                          Expanded(child: _buildPipelineCard("LUNARMATCH (RIFT2)", _comparisonData?['lunarmatch'], true)),
                        ],
                      );
                    }
                    return Column(
                      children: [
                        _buildPipelineCard("SIFT BASELINE", _comparisonData?['sift'], false),
                        const SizedBox(height: 12),
                        _buildPipelineCard("LUNARMATCH (RIFT2)", _comparisonData?['lunarmatch'], true),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 16),

                // Delta card
                _buildDeltaCard(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingCard(String message, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(fontSize: 12, color: Colors.white),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineCard(String title, Map<String, dynamic>? data, bool isLunarMatch) {
    if (data == null) {
      return _buildEmptyCard(title);
    }

    final status = data['status'] ?? 'UNKNOWN';
    final isFailed = status == 'FAILED' || status == 'NOT_RELIABLE' || status == 'REGISTRATION_NOT_RELIABLE';
    final isAccepted = status == 'ACCEPTED' || status == 'SUCCESSFUL';
    final inliers = data['inliers'] ?? 0;
    final rmsePx = data['rmse_px'];
    final coverage = data['coverage'] ?? 0.0;
    final inlierRatio = data['inlier_ratio'] ?? 0.0;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isFailed ? LunarTheme.borderFocus : (isLunarMatch ? Colors.white : LunarTheme.border),
          width: isFailed ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 0.6,
                    color: isFailed ? LunarTheme.borderFocus : Colors.white,
                  ),
                ),
              ),
              if (isFailed)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: LunarTheme.borderFocus,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    status == 'NOT_RELIABLE' || status == 'REGISTRATION_NOT_RELIABLE' ? "REJECTED" : "FAILED",
                    style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.black),
                  ),
                )
              else if (isAccepted)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text("ACCEPTED", style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: Colors.black)),
                ),
            ],
          ),
          const SizedBox(height: 10),
          _metricRow("INLIERS", "$inliers", "Geometric consensus", "RMSE", rmsePx != null && rmsePx != 0 ? Formatters.formatPixels(rmsePx.toDouble()) : "N/A", "Reprojection error"),
          const SizedBox(height: 8),
          _metricRow("COVERAGE", Formatters.formatPercentage(coverage.toDouble()), "Grid occupancy", inlierRatio > 0 ? "INLIER RATIO" : null, inlierRatio > 0 ? Formatters.formatPercentage(inlierRatio.toDouble()) : null, inlierRatio > 0 ? "Filtered matches" : null),
          if (isFailed && data['reason'] != null) ...[
            const SizedBox(height: 8),
            Text(
              data['reason'],
              style: const TextStyle(fontSize: 10, fontStyle: FontStyle.italic, color: LunarTheme.borderFocus),
            ),
          ],
        ],
      ),
    );
  }

  Widget _metricRow(
    String labelA, String valueA, String subtitleA,
    String? labelB, String? valueB, String? subtitleB,
  ) {
    final a = MetricCard(
      title: labelA,
      value: valueA,
      subtitle: subtitleA,
    );
    return labelB == null
        ? a
        : Row(
            children: [
              Expanded(child: a),
              const SizedBox(width: 8),
              Expanded(
                child: MetricCard(
                  title: labelB,
                  value: valueB!,
                  subtitle: subtitleB!,
                ),
              ),
            ],
          );
  }

  Widget _buildEmptyCard(String title) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Colors.white)),
          const SizedBox(height: 8),
          const Text("No data available", style: TextStyle(fontSize: 11, color: LunarTheme.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildDeltaCard() {
    final data = _comparisonData;
    if (data == null) return const SizedBox();

    final siftData = data['sift'] ?? {};
    final lmData = data['lunarmatch'] ?? {};
    final siftInliers = (siftData['inliers'] ?? 0) as int;
    final lmInliers = (lmData['inliers'] ?? 0) as int;
    final siftCoverage = (siftData['coverage'] ?? 0.0).toDouble();
    final lmCoverage = (lmData['coverage'] ?? 0.0).toDouble();
    final siftRmse = siftData['rmse_px'] as double?;
    final lmRmse = lmData['rmse_px'] as double?;

    final deltaInliers = lmInliers - siftInliers;
    final deltaCoverage = lmCoverage - siftCoverage;
    final deltaRmse = (siftRmse != null && lmRmse != null) ? siftRmse - lmRmse : null;

    final inlierWins = deltaInliers > 0;
    final coverageWins = deltaCoverage > 0;
    final rmseWins = deltaRmse != null && deltaRmse < 0;
    final coveragePct = (deltaCoverage * 100).toStringAsFixed(1);

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
            "DELTA: LUNARMATCH vs SIFT",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.0,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _deltaItem(
                  "+$deltaInliers inliers",
                  inlierWins,
                  Icons.arrow_upward,
                ),
              ),
              Expanded(
                child: _deltaItem(
                  "+$coveragePct% coverage",
                  coverageWins,
                  Icons.arrow_upward,
                ),
              ),
              Expanded(
                child: _deltaItem(
                  deltaRmse != null ? "\u2212${deltaRmse.abs().toStringAsFixed(2)} px RMSE" : "RMSE N/A",
                  rmseWins,
                  Icons.arrow_downward,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _deltaItem(String label, bool wins, IconData arrow) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
      decoration: BoxDecoration(
        color: wins ? Colors.white.withValues(alpha: 0.08) : LunarTheme.surfaceElevated,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: wins ? Colors.white : LunarTheme.border,
          width: 1,
        ),
      ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(arrow, size: 14, color: wins ? Colors.white : LunarTheme.textTertiary),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                color: wins ? Colors.white : LunarTheme.textTertiary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
