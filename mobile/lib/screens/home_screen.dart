import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../providers/pipeline_provider.dart';

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
                color: isOnline ? const Color(0xFF4CAF50) : const Color(0xFF777777),
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
          ],
        ),
      ),
      body: SafeArea(
        child: ScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
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
                      "Aligns Chandrayaan-2 optical imagery (OHRC, TMC-2, IIRS) against lunar reference data across Sun angles, scales, and sensors.",
                      style: TextStyle(
                        fontSize: 12,
                        color: LunarTheme.textSecondary,
                        height: 1.45,
                      ),
                    ),
                    const SizedBox(height: 14),
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
                            color: isOnline ? const Color(0xFF4CAF50) : const Color(0xFF999999),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              isOnline ? "Connected" : "Offline mode",
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ),
                          IconButton(
                            onTap: () => pipeProv.checkBackendHealth(),
                            icon: const Icon(Icons.refresh, size: 16, color: LunarTheme.textTertiary),
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

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
                title: "Image Registration",
                description: "Align reference and moving images using the LunarMatch pipeline.",
                icon: Icons.layers_outlined,
                onTap: () => Navigator.pushNamed(context, AppRoutes.upload),
              ),

              _buildDashboardCard(
                title: "Robustness Lab",
                description: "Test registration across illumination, scale, and geometric variations.",
                icon: Icons.science_outlined,
                onTap: () => Navigator.pushNamed(context, AppRoutes.robustness),
              ),

              _buildDashboardCard(
                title: "Engine Capabilities",
                description: "Feature detection, matching, verification, and quality assessment.",
                icon: Icons.verified_outlined,
                onTap: () => Navigator.pushNamed(context, AppRoutes.status),
              ),

              _buildDashboardCard(
                title: "Pipeline Architecture",
                description: "System block diagram and processing flow.",
                icon: Icons.schema_outlined,
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

  Widget _buildDashboardCard({
    required String title,
    required String description,
    required icons icon,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                  const SizedBox(height: 6),
                  Text(
                    description,
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
    );
  }
}