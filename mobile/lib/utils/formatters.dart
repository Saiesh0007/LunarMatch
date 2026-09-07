class Formatters {
  static String formatNumber(num? value, {int decimals = 1}) {
    if (value == null) return "N/A";
    return value.toStringAsFixed(decimals);
  }

  static String formatPercentage(num? value) {
    if (value == null) return "N/A";
    return "${value.toStringAsFixed(1)}%";
  }

  static String formatPixels(num? value) {
    if (value == null) return "N/A";
    return "${value.toStringAsFixed(2)} px";
  }

  static String formatMilliseconds(num? value) {
    if (value == null) return "N/A";
    return "${value.toStringAsFixed(0)} ms";
  }
}
