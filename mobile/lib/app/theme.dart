import 'package:flutter/material.dart';

class LunarTheme {
  // Canvas
  static const Color background = Color(0xFF0A0A0D);
  static const Color surfaceCard = Color(0xFF1A1A1F);
  static const Color surfaceElevated = Color(0xFF22222A);

  // Chandrayaan saffron
  static const Color primary = Color(0xFFFF6B1A);
  static const Color primaryGlow = Color(0x33FF6B1A);
  static const Color border = Color(0x40FF6B1A);
  static const Color borderLight = Color(0x22FF6B1A);

  // Text
  static const Color textPrimary = Color(0xFFF5F0E6);
  static const Color textSecondary = Color(0xFF8B8B94);
  static const Color textTertiary = Color(0xFF6B6B73);

  // Status
  static const Color success = Color(0xFF3FB950);
  static const Color warning = Color(0xFFD29922);
  static const Color error = Color(0xFFF85149);

  // Text styles
  static const TextStyle heading = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w800,
    letterSpacing: 0.3,
    color: textPrimary,
  );

  static const TextStyle label = TextStyle(
    fontSize: 10,
    fontWeight: FontWeight.w800,
    letterSpacing: 1.2,
    color: textTertiary,
  );

  static const TextStyle body = TextStyle(
    fontSize: 12,
    color: textSecondary,
    height: 1.45,
  );

  static const TextStyle mono = TextStyle(
    fontFamily: 'JetBrains Mono',
    fontFeatures: [FontFeature.tabularFigures()],
    color: textPrimary,
  );

  static ThemeData get darkTheme => ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: background,
    primaryColor: primary,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      surface: surfaceCard,
      background: background,
    ),
    fontFamily: 'Roboto',
    appBarTheme: const AppBarTheme(
      backgroundColor: background,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 15,
        fontWeight: FontWeight.w900,
        letterSpacing: 1.2,
        color: Colors.white,
      ),
      iconTheme: IconThemeData(color: Color(0xFFFF6B1A)),
    ),
  );
}
