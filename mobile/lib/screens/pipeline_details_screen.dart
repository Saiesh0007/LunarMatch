import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../app/theme.dart';
import '../models/pipeline_model.dart';
import '../providers/pipeline_provider.dart';
import '../widgets/section_header.dart';
import '../utils/animation_utils.dart';

/// Pipeline Details screen showing per-stage JSONL data from
/// match_decisions.jsonl and an optional Matcher Comparison card
/// when matcher_benchmark.json data is available.
class PipelineDetailsScreen extends StatefulWidget {
  const PipelineDetailsScreen({super.key});

  @override
  State<PipelineDetailsScreen> createState() => _PipelineDetailsScreenState();
}

class _PipelineDetailsScreenState extends State<PipelineDetailsScreen> {
  List<StageDetailModel> _stagesDetail = [];
  MatcherBenchmarkModel? _matcherBenchmark;
  bool _isLoading = true;
  String? _errorMessage;
  bool _benchmarkExpanded = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadData());
  }

  Future<void> _loadData() async {
    final pipeProv = context.read<PipelineProvider>();
    final res = pipeProv.latestResponse;
    if (res == null) {
      setState(() {
        _isLoading = false;
        _errorMessage = "No pipeline run available.";
      });
      return;
    }

    try {
      final data = await pipeProv.fetchRunResults(res.runId);

      final stagesRaw = data['stages_detail'] as List<dynamic>? ?? [];
      final stages = stagesRaw
          .map((e) => StageDetailModel.fromJson(e as Map<String, dynamic>))
          .toList();

      MatcherBenchmarkModel? benchmark;
      if (data['matcher_benchmark'] != null) {
        benchmark = MatcherBenchmarkModel.fromJson(
            data['matcher_benchmark'] as Map<String, dynamic>);
      }

      setState(() {
        _stagesDetail = stages;
        _matcherBenchmark = benchmark;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = "Could not load pipeline details: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final res = pipeProv.latestResponse;

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        titleSpacing: 0,
        title: const Text(
          "PIPELINE DETAILS",
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.8,
            color: Colors.white,
          ),
        ),
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : _errorMessage != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Text(
                        _errorMessage!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          color: LunarTheme.textSecondary,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  )
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Header card
                        if (res != null) _buildHeaderCard(res),
                        const SizedBox(height: 16),

                        // Stage timeline
                        const SectionHeader(
                          title: "STAGE TIMELINE",
                          subtitle: "Per-stage execution from match_decisions.jsonl",
                        ),
                        const SizedBox(height: 8),
                        ..._stagesDetail.asMap().entries.map((entry) =>
                            _buildStageRow(entry.value, entry.key)),
                        const SizedBox(height: 24),

                        // Matcher Comparison card (only if benchmark data present)
                        if (_matcherBenchmark != null) ...[
                          _buildMatcherComparisonCard(_matcherBenchmark!),
                          const SizedBox(height: 24),
                        ],

                        // Open Full Report button
                        if (res != null) _buildReportButton(res.runId, pipeProv),
                        const SizedBox(height: 16),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildHeaderCard(PipelineRunResponseModel res) {
    final statusColor = res.status == "SUCCESSFUL"
        ? Colors.white
        : res.status == "LOW_CONFIDENCE"
            ? LunarTheme.warning
            : LunarTheme.textTertiary;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  "RUN ${res.runId}",
                  style: LunarTheme.mono.copyWith(fontSize: 11),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: statusColor.withValues(alpha: 0.3)),
                ),
                child: Text(
                  res.status,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.6,
                    color: statusColor,
                  ),
                ),
              )
                  .animate(target: AnimationUtils.targetFor(context))
                  .scale(
                    begin: const Offset(0.5, 0.5),
                    end: const Offset(1.0, 1.0),
                    duration: 250.ms,
                    curve: Curves.easeOut,
                  ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _metaChip("MODE", res.executionMode.toUpperCase()),
              const SizedBox(width: 12),
              _metaChip("STAGES", "${_stagesDetail.length}"),
              const SizedBox(width: 12),
              _metaChip("TOTAL",
                  "${res.metrics.runtimeMs.toStringAsFixed(0)} ms"),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metaChip(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 9,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.6,
            color: LunarTheme.textTertiary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: LunarTheme.mono.copyWith(fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildStageRow(StageDetailModel stage, int index) {
    final hasOk = stage.ok != null;
    final passed = stage.ok == true;
    final hasFallback = stage.fallback == true;

    // Status icon
    Widget statusIcon;
    Color nameColor;
    if (hasOk && passed) {
      statusIcon = const Icon(Icons.check_circle, size: 16, color: Colors.white);
      nameColor = Colors.white;
    } else if (hasOk && !passed) {
      statusIcon = Icon(Icons.cancel, size: 16, color: LunarTheme.textTertiary);
      nameColor = LunarTheme.textTertiary;
    } else {
      statusIcon = const Icon(Icons.circle_outlined, size: 16, color: LunarTheme.textSecondary);
      nameColor = Colors.white;
    }
    statusIcon = statusIcon
        .animate(target: AnimationUtils.targetFor(context))
        .scale(
          begin: const Offset(0.5, 0.5),
          end: const Offset(1.0, 1.0),
          duration: 250.ms,
          curve: Curves.easeOut,
        );

    // Readable stage name
    final displayName = _formatStageName(stage.stage);

    // Build detail chips from extras
    final detailChips = <Widget>[];
    for (final entry in stage.extras.entries) {
      if (entry.key == 'ok') continue; // already shown via icon
      final val = entry.value;
      if (val == null) continue;
      String displayVal;
      if (val is double) {
        displayVal = val.toStringAsFixed(2);
      } else if (val is bool) {
        displayVal = val ? "yes" : "no";
      } else {
        displayVal = val.toString();
      }
      if (displayVal.length > 40) {
        displayVal = "${displayVal.substring(0, 37)}...";
      }
      detailChips.add(
        Padding(
          padding: const EdgeInsets.only(right: 8, top: 2),
          child: Text(
            "${entry.key}: $displayVal",
            style: const TextStyle(
              fontSize: 10,
              color: LunarTheme.textTertiary,
              fontFamily: 'Courier',
            ),
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: LunarTheme.surfaceCard,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: hasFallback
                ? LunarTheme.borderLight
                : LunarTheme.border,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Stage number
                Container(
                  width: 26,
                  height: 20,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: LunarTheme.surfaceElevated,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: LunarTheme.border),
                  ),
                  child: Text(
                    "${index + 1}".padLeft(2, '0'),
                    style: LunarTheme.mono.copyWith(
                      fontSize: 9,
                      color: LunarTheme.textTertiary,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                // Stage name
                Expanded(
                  child: Text(
                    displayName,
                    style: TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.4,
                      color: nameColor,
                    ),
                  ),
                ),
                // Duration
                if (stage.ms != null) ...[
                  Text(
                    "${stage.ms!.toStringAsFixed(0)} ms",
                    style: LunarTheme.mono.copyWith(
                      fontSize: 10,
                      color: LunarTheme.textTertiary,
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                // Status icon
                SizedBox(width: 20, child: Center(child: statusIcon)),
              ],
            ),
            // Reason (if present)
            if (stage.reason != null && stage.reason!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                stage.reason!,
                style: const TextStyle(
                  fontSize: 10.5,
                  color: LunarTheme.textSecondary,
                ),
              ),
            ],
            // Detail chips
            if (detailChips.isNotEmpty) ...[
              const SizedBox(height: 4),
              Wrap(children: detailChips),
            ],
          ],
        ),
      ),
    )
        .animate(
          target: AnimationUtils.targetFor(context),
          delay: (index.clamp(0, 10) * 50).ms,
        )
        .fadeIn(duration: 200.ms, curve: Curves.easeOut);
  }

  String _formatStageName(String stage) {
    return stage.toUpperCase().replaceAll('_', ' ');
  }

  Widget _buildMatcherComparisonCard(MatcherBenchmarkModel benchmark) {
    return Container(
      decoration: BoxDecoration(
        color: LunarTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunarTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Collapsible header
          InkWell(
            onTap: () => setState(() => _benchmarkExpanded = !_benchmarkExpanded),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "MATCHER COMPARISON",
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 1.0,
                            color: Colors.white,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          "Benchmarked on demo pairs",
                          style: TextStyle(
                            fontSize: 11,
                            color: LunarTheme.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    _benchmarkExpanded
                        ? Icons.keyboard_arrow_up
                        : Icons.keyboard_arrow_down,
                    color: LunarTheme.textTertiary,
                    size: 20,
                  ),
                ],
              ),
            ),
          ),

          // Collapsible body with smooth 250 ms height expansion
          AnimatedSize(
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeInOut,
            child: _benchmarkExpanded
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Divider(height: 1, color: LunarTheme.border),
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Table
                            _buildBenchmarkTable(benchmark),
                            const SizedBox(height: 16),

                            // Explanation text
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: LunarTheme.surfaceElevated,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: LunarTheme.border),
                              ),
                              child: const Text(
                                "RIFT2 + BF is the shipped matcher. On multi-modal lunar "
                                "phase-congruency features it achieves 100% success in 2.9 s on "
                                "CPU. SuperGlue and LightGlue (pretrained on natural image "
                                "datasets MegaDepth and ScanNet) do not transfer to the "
                                "phase-congruency domain without retraining. LoFTR succeeds "
                                "(detector-free, learns its own features) but at 27.5 s on CPU "
                                "exceeds the demo budget by 14x. RIFT2 is shipped for these "
                                "reasons, consistent with the MultiResSAR benchmark "
                                "(arXiv 2502.01002v1, Sec. V) which reports RIFT at 66.5% "
                                "success on SAR-optical pairs where most deep methods fall "
                                "below 50%.",
                                style: TextStyle(
                                  fontSize: 10.5,
                                  height: 1.5,
                                  color: LunarTheme.textSecondary,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  )
                : const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }

  Widget _buildBenchmarkTable(MatcherBenchmarkModel benchmark) {
    return Table(
      border: TableBorder.all(color: LunarTheme.border, width: 0.5),
      columnWidths: const {
        0: FlexColumnWidth(2.2),
        1: FlexColumnWidth(1.2),
        2: FlexColumnWidth(1.2),
        3: FlexColumnWidth(1.5),
        4: FlexColumnWidth(2.0),
      },
      children: [
        // Header row
        TableRow(
          decoration: BoxDecoration(color: LunarTheme.surfaceElevated),
          children: [
            _tableHeader("Matcher"),
            _tableHeader("Success"),
            _tableHeader("RMSE (px)"),
            _tableHeader("Time (ms)"),
            _tableHeader("Notes"),
          ],
        ),
        // Data rows with staggered fade-in top to bottom
        ...benchmark.matchers.asMap().entries.map((e) => _buildMatcherRow(e.value, e.key)),
      ],
    );
  }

  Widget _tableHeader(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 9.5,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.5,
          color: Colors.white,
        ),
      ),
    );
  }

  TableRow _buildMatcherRow(MatcherResultModel m, int rowIndex) {
    final isSkipped = m.skipped;
    final textColor = isSkipped ? LunarTheme.textTertiary : Colors.white;
    final cellStyle = TextStyle(
      fontSize: 10,
      fontFamily: 'Courier',
      color: textColor,
    );
    final animTarget = AnimationUtils.targetFor(context);

    return TableRow(
      decoration: BoxDecoration(
        color: isSkipped
            ? LunarTheme.surfaceElevated.withValues(alpha: 0.5)
            : Colors.transparent,
      ),
      children: [
        _tableCell(m.name, cellStyle, animTarget, rowIndex),
        _tableCell(
          isSkipped
              ? "—"
              : m.successRate != null
                  ? "${(m.successRate! * 100).toStringAsFixed(0)}%"
                  : "—",
          cellStyle,
          animTarget,
          rowIndex,
        ),
        _tableCell(
          isSkipped
              ? "—"
              : m.meanRmsePx?.toStringAsFixed(2) ?? "—",
          cellStyle,
          animTarget,
          rowIndex,
        ),
        _tableCell(
          isSkipped
              ? "—"
              : m.meanTimeMs?.toStringAsFixed(0) ?? "—",
          cellStyle,
          animTarget,
          rowIndex,
        ),
        _tableCell(
          isSkipped
              ? (m.reason ?? "Not deployed")
              : (m.notes ?? ""),
          TextStyle(
            fontSize: 10,
            color: isSkipped ? LunarTheme.textTertiary : LunarTheme.textSecondary,
          ),
          animTarget,
          rowIndex,
        ),
      ],
    );
  }

  Widget _tableCell(String text, TextStyle style, [double? animTarget, int rowIndex = 0]) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      child: Text(text, style: style),
    )
        .animate(target: animTarget, delay: (rowIndex * 50).ms)
        .fadeIn(duration: 200.ms, curve: Curves.easeOut);
  }

  Widget _buildReportButton(String runId, PipelineProvider pipeProv) {
    return OutlinedButton.icon(
      onPressed: () async {
        try {
          final report = await pipeProv.fetchRunReport(runId);
          if (mounted) {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                backgroundColor: LunarTheme.surfaceCard,
                title: const Text(
                  "FULL REPORT",
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                    color: Colors.white,
                  ),
                ),
                content: SingleChildScrollView(
                  child: Text(
                    report,
                    style: LunarTheme.mono.copyWith(fontSize: 10),
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text("CLOSE"),
                  ),
                ],
              ),
            );
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text("Error fetching report: $e")),
            );
          }
        }
      },
      icon: const Icon(Icons.description_outlined, size: 16),
      label: const Text(
        "OPEN FULL INSIGHT REPORT",
        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.5),
      ),
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 14),
        foregroundColor: Colors.white,
        side: const BorderSide(color: LunarTheme.borderLight),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    )
        .animate(target: AnimationUtils.targetFor(context))
        .fadeIn(duration: 300.ms, curve: Curves.easeOut)
        .slideY(begin: 0.15, end: 0, duration: 300.ms, curve: Curves.easeOut);
  }
}
