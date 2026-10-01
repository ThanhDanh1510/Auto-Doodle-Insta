"""
Color quantization and thresholding engine using OpenCV and K-Means.
"""

from typing import List, Tuple
import cv2
import numpy as np

try:
    from src.core.models import RGBColor
except (ImportError, ModuleNotFoundError):
    from core.models import RGBColor  # type: ignore


def quantize_colors_kmeans(
    image_bgr: np.ndarray, num_colors: int = 12
) -> Tuple[np.ndarray, List[RGBColor], np.ndarray, np.ndarray]:
    """
    Quantizes an input BGR image into num_colors dominant colors using K-Means clustering.
    Returns: (quantized_image_bgr, palette_rgb_list, labels_2d, centers_bgr)
    """
    h, w, _ = image_bgr.shape
    pixels = np.ascontiguousarray(image_bgr.reshape((-1, 3)), dtype=np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    flags = cv2.KMEANS_PP_CENTERS
    best_labels = np.empty((0, 1), dtype=np.int32)

    _, labels, centers = cv2.kmeans(pixels, num_colors, best_labels, criteria, 10, flags)

    centers_uint8 = centers.astype(np.uint8)
    quantized_pixels = centers_uint8[labels.flatten()]
    quantized_image = quantized_pixels.reshape((h, w, 3))

    labels_2d = labels.reshape((h, w))

    palette_rgb: List[RGBColor] = []
    for center in centers_uint8:
        palette_rgb.append((int(center[2]), int(center[1]), int(center[0])))

    return quantized_image, palette_rgb, labels_2d, centers_uint8


def is_near_white(rgb: RGBColor, threshold: int = 240) -> bool:
    """Check if a color is close enough to white to skip drawing on white canvas."""
    r, g, b = rgb
    return r >= threshold and g >= threshold and b >= threshold
