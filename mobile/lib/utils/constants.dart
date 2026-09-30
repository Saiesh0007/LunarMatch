class AppConstants {
  static const String appName = "LunarMatch";
  static const String appSubtitle = "Multi-Modal Lunar Image Correspondence & Registration";
  static const String engineName = "LunarMatch";
  static const String problemStatement = "Smart India Hackathon 2026 | PS: 26166";
  static const String organization = "ISRO (Indian Space Research Organisation)";
  static const String teamName = "Team LunarMatch";
  static const String domain = "Space Technology";

  // Default API configuration
  // For Android Emulator: "http://10.0.2.2:8000"
  // For Windows Desktop / Web: "http://127.0.0.1:8000"
  static const String defaultLocalApiUrl = "http://127.0.0.1:8000";
  static const String defaultEmulatorApiUrl = "http://10.0.2.2:8000";

  // Fixed deterministic simulation seed
  static const int simulationSeed = 26166;

  // Sensor Options
  static const List<String> sensorList = [
    "OHRC",
    "TMC",
    "TMC-2",
    "IIRS",
    "LRO NAC",
    "SELENE",
    "Other",
  ];
}
