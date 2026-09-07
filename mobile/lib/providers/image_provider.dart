import 'package:flutter/material.dart';
import '../models/image_model.dart';
import '../services/image_service.dart';

class LunarImageProvider with ChangeNotifier {
  LunarImageModel? _referenceImage;
  LunarImageModel? _movingImage;

  String _referenceSensor = "OHRC";
  String _movingSensor = "TMC-2";

  DemoPairModel? _selectedDemoPair;

  LunarImageModel? get referenceImage => _referenceImage;
  LunarImageModel? get movingImage => _movingImage;
  String get referenceSensor => _referenceSensor;
  String get movingSensor => _movingSensor;
  DemoPairModel? get selectedDemoPair => _selectedDemoPair;

  bool get hasBothImages => _referenceImage != null && _movingImage != null;

  void setReferenceSensor(String sensor) {
    _referenceSensor = sensor;
    if (_referenceImage != null) {
      _referenceImage = _referenceImage!.copyWith(sensor: sensor);
    }
    notifyListeners();
  }

  void setMovingSensor(String sensor) {
    _movingSensor = sensor;
    if (_movingImage != null) {
      _movingImage = _movingImage!.copyWith(sensor: sensor);
    }
    notifyListeners();
  }

  void setReferenceImage(LunarImageModel img) {
    _referenceImage = img;
    _selectedDemoPair = null;
    notifyListeners();
  }

  void setMovingImage(LunarImageModel img) {
    _movingImage = img;
    _selectedDemoPair = null;
    notifyListeners();
  }

  Future<void> loadDemoPair(DemoPairModel pair) async {
    _selectedDemoPair = pair;
    _referenceSensor = pair.referenceSensor;
    _movingSensor = pair.movingSensor;

    _referenceImage = await ImagePickerService.loadBundledDemoImage(
      assetPath: pair.referenceAssetPath,
      imageId: pair.referenceImageId,
      name: "Reference Image (${pair.referenceSensor})",
      sensor: pair.referenceSensor,
    );

    _movingImage = await ImagePickerService.loadBundledDemoImage(
      assetPath: pair.movingAssetPath,
      imageId: pair.movingImageId,
      name: "Moving Image (${pair.movingSensor})",
      sensor: pair.movingSensor,
    );

    notifyListeners();
  }

  /// Swap images while strictly preserving the scientific definitions:
  /// Reference is ALWAYS the fixed coordinate frame.
  /// Moving is ALWAYS the image that gets transformed.
  void swapImages() {
    if (_referenceImage == null && _movingImage == null) return;

    final tempImg = _referenceImage;
    final tempSensor = _referenceSensor;

    _referenceImage = _movingImage;
    _referenceSensor = _movingSensor;

    _movingImage = tempImg;
    _movingSensor = tempSensor;

    notifyListeners();
  }

  void clearImages() {
    _referenceImage = null;
    _movingImage = null;
    _selectedDemoPair = null;
    notifyListeners();
  }
}
