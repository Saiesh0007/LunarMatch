import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../providers/pipeline_provider.dart';
import '../widgets/status_badge.dart';
import '../widgets/responsive_badge.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _bottomNavIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();
    final isOnline = pipeProv.isBackendConnected;

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        titleSpacing: 12,
        title: Row(
          children: [
            // Logo displayed cleanly on black background without white circular container
            Image.asset(
              'assets/icons/app_logo.png',
              width: 24,
              height: 24,
              fit: BoxFit.contain,
            ),
            const SizedBox(width: 6),
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: isOnline ? Colors.white : const Color(0xFF777777),
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            const Expanded(
              child: Text(
                "LUNARMATCH",
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.2,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 8),
            StatusBadge(mode: pipeProv.currentExecutionModeLabel),
          ],
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Mission Control Banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: LunarTheme.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 8,
                      runSpacing: 4,
                      children: const [
                        Text(
                          "ISRO — PROBLEM STATEMENT 26166",
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                            color: Colors.white,
                          ),
                        ),
                        ResponsiveBadge(
                          label: "TEAM LUNARMATCH",
                          variant: BadgeVariant.subtle,
                          fontSize: 8.5,
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      "Lunar Image Correspondence & Registration Engine",
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.3,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      "Aligns heterogeneous multi-modal lunar observation sets under extreme illumination variations, scale differentials, and spatial crater clustering.",
                      style: TextStyle(
                        fontSize: 12,
                        color: LunarTheme.textSecondary,
                        height: 1.45,
                      ),
                    ),
                    const SizedBox(height: 14),

                    // Backend Connectivity Bar
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: LunarTheme.surfaceElevated,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: LunarTheme.border),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            isOnline ? Icons.cloud_done_outlined : Icons.offline_bolt_outlined,
                            size: 15,
                            color: isOnline ? Colors.white : const Color(0xFF999999),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              isOnline ? "Backend: FASTAPI ONLINE" : "Backend: LOCAL FALLBACK",
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          InkWell(
                            onTap: () => pipeProv.checkBackendHealth(),
                            borderRadius: BorderRadius.circular(4),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: const Color(0xFF222222),
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: LunarTheme.borderLight),
                              ),
                              child: const Text(
                                "CHECK",
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Action Cards Title
              const Text(
                "CORE CAPABILITIES",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                  color: LunarTheme.textTertiary,
                ),
              ),
              const SizedBox(height: 10),

              _buildDashboardCard(
                title: "COMPARE SIFT vs LUNARMATCH",
                subtitle: "Side-by-side comparison of SIFT baseline vs LunarMatch RIFT2 on the same input pair with delta metrics.",
                icon: Icons.compare_outlined,
                badgeText: "DEMO SCREEN",
                onTap: () => Navigator.pushNamed(context, AppRoutes.comparison),
              ),

              _buildDashboardCard(
                title: "SEE FAILURE DETECTION",
                subtitle: "When LunarMatch says NO: rejection criteria, honest diagnostics, and trustworthiness metrics.",
                icon: Icons.error_outline,
                badgeText: "HONESTY DEMO",
                onTap: () => Navigator.pushNamed(context, AppRoutes.failureCase),
              ),

              _buildDashboardCard(
                title: "IMAGE REGISTRATION",
                subtitle: "Select Reference (Fixed) and Moving images, configure preprocessing, and run registration pipeline.",
                icon: Icons.layers_outlined,
                badgeText: "PRIMARY WORKFLOW",
                onTap: () => Navigator.pushNamed(context, AppRoutes.upload),
              ),

              _buildDashboardCard(
                title: "ROBUSTNESS LABORATORY",
                subtitle: "Execute controlled prototype experiments: sweep illumination delta, scale variation, and geometric transformations.",
                icon: Icons.science_outlined,
                badgeText: "PROFILING STUDIO",
                onTap: () => Navigator.pushNamed(context, AppRoutes.robustness),
              ),

              _buildDashboardCard(
                title: "ENGINE CAPABILITIES",
                subtitle: "Scientifically honest capability matrix: clearly delineates Verified, Demo, and Research Roadmap components.",
                icon: Icons.verified_outlined,
                badgeText: "TECHNICAL AUDIT",
                onTap: () => Navigator.pushNamed(context, AppRoutes.status),
              ),

              _buildDashboardCard(
                title: "PIPELINE ARCHITECTURE",
                subtitle: "Interactive block diagram comparing the Current MVP baseline with the Target Research Architecture.",
                icon: Icons.schema_outlined,
                badgeText: "SPECIFICATION",
                onTap: () => Navigator.pushNamed(context, AppRoutes.architecture),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            border: Border(top: BorderSide(color: LunarTheme.border, width: 1)),
          ),
          child: NavigationBar(
            selectedIndex: _bottomNavIndex,
            backgroundColor: LunarTheme.background,
            surfaceTintColor: Colors.transparent,
            indicatorColor: const Color(0xFF222222),
            onDestinationSelected: (idx) {
              setState(() => _bottomNavIndex = idx);
              if (idx == 1) Navigator.pushNamed(context, AppRoutes.upload);
              if (idx == 2) Navigator.pushNamed(context, AppRoutes.robustness);
              if (idx == 3) Navigator.pushNamed(context, AppRoutes.about);
            },
            destinations: const [
              NavigationDestination(
                icon: Icon(Icons.home_outlined),
                selectedIcon: Icon(Icons.home),
                label: "Home",
              ),
              NavigationDestination(
                icon: Icon(Icons.layers_outlined),
                selectedIcon: Icon(Icons.layers),
                label: "Register",
              ),
              NavigationDestination(
                icon: Icon(Icons.science_outlined),
                selectedIcon: Icon(Icons.science),
                label: "Lab",
              ),
              NavigationDestination(
                icon: Icon(Icons.info_outline),
                selectedIcon: Icon(Icons.info),
                label: "About",
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Responsive dashboard card:
  /// Places badge neatly below the title to completely prevent horizontal clipping/overflow.
  Widget _buildDashboardCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required String badgeText,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon container with clean monochrome styling
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: LunarTheme.surfaceElevated,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: LunarTheme.borderLight),
                ),
                child: Icon(icon, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 14),

              // Text content and badge
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.6,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    ResponsiveBadge(
                      label: badgeText,
                      variant: BadgeVariant.standard,
                      fontSize: 8.5,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        fontSize: 11,
                        color: LunarTheme.textSecondary,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right, size: 18, color: LunarTheme.textTertiary),
            ],
          ),
        ),
      ),
    );
  }
}
