"""
Contour point reduction using Ramer-Douglas-Peucker (RDP) algorithm.
"""

from typing import List
import cv2
import numpy as np

try:
    from src.core.models import ContourPoints, Point2D
except (ImportError, ModuleNotFoundError):
    from core.models import ContourPoints, Point2D  # type: ignore


def simplify_contour(cnt: np.ndarray, epsilon_val: float) -> ContourPoints:
    """
    Simplifies dense contour points using cv2.approxPolyDP.
    Returns a list of integer (x, y) coordinate tuples.
    """
    if epsilon_val <= 0:
        return [(int(p[0][0]), int(p[0][1])) for p in cnt]
    approx = cv2.approxPolyDP(cnt, epsilon_val, False)
    return [(int(p[0][0]), int(p[0][1])) for p in approx]
