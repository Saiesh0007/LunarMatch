import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../app/theme.dart';
import '../app/routes.dart';
import '../providers/pipeline_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final pipeProv = context.watch<PipelineProvider>();

    return Scaffold(
      backgroundColor: LunarTheme.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunarTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Settings"),
        centerTitle: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Application section
              _buildSection("APPLICATION", [
                _buildSettingsTile(
                  title: "Theme",
                  subtitle: "System default (Dark)",
                  trailing: const Icon(Icons.brightness_6, color: LunarTheme.textTertiary),
                  onTap: () {},
                ),
                _buildSettingsTile(
                  title: "Language",
                  subtitle: "English",
                  trailing: const Icon(Icons.language, color: LunarTheme.textTertiary),
                  onTap: () {},
                ),
                _buildSettingsTile(
                  title: "Units",
                  subtitle: "Metric (px, mm, degrees)",
                  trailing: const Icon(Icons.straighten, color: LunarTheme.textTertiary),
                  onTap: () {},
                ),
              ]),
              const SizedBox(height: 24),

              // System section
              _buildSection("SYSTEM", [
                _buildSettingsTile(
                  title: "Backend API URL",
                  subtitle: pipeProv.apiBaseUrl,
                  trailing: const Icon(Icons.cloud_outlined, color: LunarTheme.textTertiary),
                  onTap: () => _showApiUrlDialog(context, pipeProv),
                ),
                _buildSwitchTile(
                  title: "Force Demo Mode",
                  subtitle: "Use local simulation when offline",
                  value: pipeProv.forceLocalDemo,
                  onChanged: (v) => pipeProv.toggleLocalDemoMode(v),
                ),
                _buildSwitchTile(
                  title: "Auto-save Results",
                  subtitle: "Persist registration history locally",
                  value: true,
                  onChanged: (v) {},
                ),
                _buildSwitchTile(
                  title: "Debug Logging",
                  subtitle: "Verbose pipeline telemetry",
                  value: false,
                  onChanged: (v) {},
                ),
              ]),
              const SizedBox(height: 24),

              // About section
              _buildSection("ABOUT", [
                _buildSettingsTile(
                  title: "Version",
                  subtitle: "1.0.0 (Build 26166)",
                  trailing: const Icon(Icons.info_outline, color: LunarTheme.textTertiary),
                  onTap: () => Navigator.pushNamed(context, AppRoutes.about),
                ),
                _buildSettingsTile(
                  title: "Licenses",
                  subtitle: "Open source dependencies",
                  trailing: const Icon(Icons.description_outlined, color: LunarTheme.textTertiary),
                  onTap: () {},
                ),
                _buildSettingsTile(
                  title: "Privacy Policy",
                  subtitle: "No telemetry collected",
                  trailing: const Icon(Icons.privacy_tip_outlined, color: LunarTheme.textTertiary),
                  onTap: () {},
                ),
              ]),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.2,
            color: LunarTheme.textTertiary,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: LunarTheme.surfaceCard,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: LunarTheme.border),
          ),
          child: Column(children: children),
        ),
      ],
    );
  }

  Widget _buildSettingsTile({
    required String title,
    required String subtitle,
    required Widget trailing,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(color: LunarTheme.borderLight, width: 1),
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: LunarTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                  ),
                ],
              ),
            ),
            trailing,
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: LunarTheme.borderLight, width: 1),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: LunarTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 11, color: LunarTheme.textSecondary),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            activeColor: Colors.black,
            activeTrackColor: LunarTheme.primary,
            inactiveThumbColor: LunarTheme.textSecondary,
            inactiveTrackColor: LunarTheme.surfaceElevated,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  void _showApiUrlDialog(BuildContext context, PipelineProvider pipeProv) {
    final controller = TextEditingController(text: pipeProv.apiBaseUrl);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: LunarTheme.surfaceCard,
        title: const Text("Backend API URL", style: TextStyle(color: LunarTheme.textPrimary)),
        content: TextField(
          controller: controller,
          style: const TextStyle(color: LunarTheme.textPrimary),
          decoration: InputDecoration(
            hintText: "http://192.168.x.x:8000",
            hintStyle: TextStyle(color: LunarTheme.textTertiary),
            filled: true,
            fillColor: LunarTheme.surfaceElevated,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: LunarTheme.border),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel", style: TextStyle(color: LunarTheme.textSecondary)),
          ),
          ElevatedButton(
            onPressed: () {
              pipeProv.setBaseUrl(controller.text.trim());
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: LunarTheme.primary,
              foregroundColor: Colors.black,
            ),
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }
}