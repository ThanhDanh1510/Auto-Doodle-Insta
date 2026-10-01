"""
Color space conversions (RGB <-> CIE-Lab) and perceptual Delta-E distance matching.
"""

from typing import List, Tuple
import cv2
import numpy as np

try:
    from src.core.models import ContourPoints, RGBColor
except (ImportError, ModuleNotFoundError):
    from core.models import ContourPoints, RGBColor  # type: ignore


def rgb_to_lab(rgb_color: RGBColor) -> np.ndarray:
    """Converts an RGB tuple (R, G, B) to CIE-Lab float32 vector."""
    bgr_pixel = np.array([[[rgb_color[2], rgb_color[1], rgb_color[0]]]], dtype=np.uint8)
    lab_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2LAB)
    return lab_pixel[0][0].astype(np.float32)


def color_distance_lab(rgb1: RGBColor, rgb2: RGBColor) -> float:
    """Calculates perceptual Euclidean distance (Delta-E) in CIE-Lab color space."""
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    return float(np.linalg.norm(lab1 - lab2))


def sample_contour_color(image_bgr: np.ndarray, contour: ContourPoints) -> RGBColor:
    """
    Samples pixels from the source image along the given contour points
    and returns the average RGB color tuple.
    """
    h, w, _ = image_bgr.shape
    sampled_colors: List[Tuple[int, int, int]] = []
    step = max(1, len(contour) // 20)
    for i in range(0, len(contour), step):
        pt = contour[i]
        px, py = pt[0], pt[1]
        if 0 <= px < w and 0 <= py < h:
            bgr = image_bgr[py, px]
            sampled_colors.append((int(bgr[2]), int(bgr[1]), int(bgr[0])))

    if not sampled_colors:
        return (0, 0, 0)

    avg_r = int(np.mean([c[0] for c in sampled_colors]))
    avg_g = int(np.mean([c[1] for c in sampled_colors]))
    avg_b = int(np.mean([c[2] for c in sampled_colors]))
    return (avg_r, avg_g, avg_b)
