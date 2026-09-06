import cv2
import numpy as np


def register(reference, moving, transform, model="affine"):
    h, w = reference.shape[:2]

    if model == "affine":
        registered = cv2.warpAffine(moving, transform, (w, h))
    elif model == "homography":
        registered = cv2.warpPerspective(moving, transform, (w, h))
    else:
        raise ValueError(f"Unknown model: {model}. Available: affine, homography")

    return registered


def create_overlay(reference, registered, alpha=0.5):
    ref_display = reference
    reg_display = registered

    if ref_display.ndim == 2:
        ref_display = cv2.cvtColor(ref_display, cv2.COLOR_GRAY2BGR)
    if reg_display.ndim == 2:
        reg_display = cv2.cvtColor(reg_display, cv2.COLOR_GRAY2BGR)

    if ref_display.shape != reg_display.shape:
        reg_display = cv2.resize(reg_display, (ref_display.shape[1], ref_display.shape[0]))

    return cv2.addWeighted(ref_display, alpha, reg_display, 1 - alpha, 0)


def create_difference(reference, registered):
    ref_gray = reference if reference.ndim == 2 else cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    reg_gray = registered if registered.ndim == 2 else cv2.cvtColor(registered, cv2.COLOR_BGR2GRAY)

    if ref_gray.shape != reg_gray.shape:
        reg_gray = cv2.resize(reg_gray, (ref_gray.shape[1], ref_gray.shape[0]))

    return cv2.absdiff(ref_gray, reg_gray)
