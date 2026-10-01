"""
Edge detection filters and raw contour extraction algorithms.
"""

from typing import Sequence, Tuple
import cv2
import numpy as np


def extract_raw_contours(
    image_bgr: np.ndarray,
    mode: str = "canny",
    canny_lower: int = 50,
    canny_upper: int = 150,
    blur_kernel: int = 5,
) -> Tuple[Sequence[np.ndarray], int]:
    """
    Applies image preprocessing and extracts raw contours based on the selected edge mode.
    Modes: "canny", "bilateral", "adaptive".
    Returns: (raw_contours, original_point_count)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_k = max(1, blur_kernel)
    if blur_k % 2 == 0:
        blur_k += 1

    if mode == "bilateral":
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.Canny(filtered, canny_lower, canny_upper)
    elif mode == "adaptive":
        blurred = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        edges = cv2.Canny(binary, canny_lower, canny_upper)
    else:  # Standard Canny
        blurred = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
        edges = cv2.Canny(blurred, canny_lower, canny_upper)

    raw_contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    original_point_count = sum(len(c) for c in raw_contours)
    return raw_contours, original_point_count
