import 'package:flutter/material.dart';
import '../app/theme.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final history = _getMockHistory();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("History"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: const Text(
                  "REGISTRATION HISTORY",
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.0,
                    color: LunarTheme.textPrimary,
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Table
              Container(
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  children: [
                    // Header row
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: LunarTheme.surfaceElevated,
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(12),
                          topRight: Radius.circular(12),
                        ),
                        border: Border(
                          bottom: BorderSide(color: LunarTheme.border, width: 1),
                        ),
                      ),
                      child: Row(
                        children: [
                          _buildTableHeader("Date", flex: 2),
                          _buildTableHeader("Pair", flex: 2),
                          _buildTableHeader("Method", flex: 2),
                          _buildTableHeader("Inliers", flex: 1),
                          _buildTableHeader("RMSE", flex: 1),
                          _buildTableHeader("Decision", flex: 2),
                        ],
                      ),
                    ),
                    // Data rows
                    ...history.asMap().entries.map((entry) {
                      final idx = entry.key;
                      final item = entry.value;
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: LunarTheme.borderLight,
                              width: idx == history.length - 1 ? 0 : 1,
                            ),
                          ),
                        ),
                        child: Row(
                          children: [
                            _buildTableCell(item["date"]!, flex: 2, mono: true),
                            _buildTableCell(item["pair"]!, flex: 2),
                            _buildTableCell(item["method"]!, flex: 2, mono: true),
                            _buildTableCell(item["inliers"]!, flex: 1, mono: true, align: TextAlign.center),
                            _buildTableCell(item["rmse"]!, flex: 1, mono: true, align: TextAlign.center),
                            _buildTableCell(
                              item["decision"]!,
                              flex: 2,
                              align: TextAlign.center,
                              badgeColor: item["decision"] == "RELIABLE" ? LunarTheme.success : LunarTheme.error,
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTableHeader(String text, {required int flex}) {
    return Expanded(
      flex: flex,
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          letterSpacing: 1.2,
          color: LunarTheme.textTertiary,
        ),
      ),
    );
  }

  Widget _buildTableCell(String text,
      {required int flex,
      bool mono = false,
      TextAlign align = TextAlign.left,
      Color? badgeColor}) {
    Widget content;
    if (badgeColor != null) {
      content = Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          color: badgeColor.withOpacity(0.2),
          borderRadius: BorderRadius.circular(4),
          border: Border.all(color: badgeColor, width: 1),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            color: badgeColor,
          ),
        ),
      );
    } else if (mono) {
      content = Text(
        text,
        style: LunarTheme.mono.copyWith(fontSize: 11, color: LunarTheme.textPrimary),
        textAlign: align,
      );
    } else {
      content = Text(
        text,
        style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
        textAlign: align,
      );
    }

    return Expanded(
      flex: flex,
      child: Align(alignment: _getAlignment(align), child: content),
    );
  }

  Alignment _getAlignment(TextAlign align) {
    switch (align) {
      case TextAlign.center:
        return Alignment.center;
      case TextAlign.right:
        return Alignment.centerRight;
      default:
        return Alignment.centerLeft;
    }
  }

  List<Map<String, String>> _getMockHistory() {
    return [
      {
        "date": "2026-09-14 14:32",
        "pair": "Pair A (OHRC/TMC-2)",
        "method": "RIFT2+MAGSAC++",
        "inliers": "1,243",
        "rmse": "1.18 px",
        "decision": "RELIABLE",
      },
      {
        "date": "2026-09-14 13:45",
        "pair": "Pair B (LRO/IIRS)",
        "method": "SIFT+BF",
        "inliers": "847",
        "rmse": "2.34 px",
        "decision": "RELIABLE",
      },
      {
        "date": "2026-09-14 12:18",
        "pair": "Pair C (Custom)",
        "method": "RIFT2+MAGSAC++",
        "inliers": "18",
        "rmse": "5.67 px",
        "decision": "UNRELIABLE",
      },
      {
        "date": "2026-09-13 18:22",
        "pair": "Pair A (OHRC/TMC-2)",
        "method": "SuperPoint",
        "inliers": "2,104",
        "rmse": "0.92 px",
        "decision": "RELIABLE",
      },
      {
        "date": "2026-09-13 16:05",
        "pair": "Pair D (Synthetic)",
        "method": "SIFT+BF",
        "inliers": "312",
        "rmse": "4.21 px",
        "decision": "UNRELIABLE",
      },
    ];
  }
}