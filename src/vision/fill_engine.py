"""
Dense scanline zig-zag filling and layer contour generation for region masks.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

try:
    from src.core.models import ContourPoints
    from src.vision.quantizer import is_near_white, quantize_colors_kmeans
except (ImportError, ModuleNotFoundError):
    from core.models import ContourPoints  # type: ignore
    from vision.quantizer import is_near_white, quantize_colors_kmeans  # type: ignore


def generate_fill_strokes_for_mask(mask: np.ndarray, step: int = 2) -> List[ContourPoints]:
    """
    Generate dense horizontal fill strokes for a binary region mask.
    Uses step (default 2px) for near-pixel-perfect fill coverage.
    Alternates direction (zig-zag) to minimize pen-up movement.
    """
    h, w = mask.shape
    strokes: List[ContourPoints] = []

    # Clean up mask with morphological close to reduce tiny gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    direction = 1  # 1 = left-to-right, -1 = right-to-left (zig-zag)
    for y in range(0, h, step):
        row = cleaned[y, :]
        diff = np.diff(np.int32(row != 0))
        starts = np.where(diff == 1)[0] + 1
        ends = np.where(diff == -1)[0] + 1

        if row[0] != 0:
            starts = np.r_[0, starts]
        if row[-1] != 0:
            ends = np.r_[ends, w - 1]

        row_strokes: List[ContourPoints] = []
        for s_x, e_x in zip(starts, ends):
            if e_x - s_x >= 2:
                stroke: ContourPoints = []
                if direction == 1:
                    for x in range(s_x, e_x + 1):
                        stroke.append((x, y))
                else:
                    for x in range(e_x, s_x - 1, -1):
                        stroke.append((x, y))
                if stroke:
                    row_strokes.append(stroke)

        strokes.extend(row_strokes)
        direction *= -1  # Zig-zag between rows

    return strokes


def generate_edge_strokes_for_mask(mask: np.ndarray, epsilon: float = 1.2) -> List[ContourPoints]:
    """Generate edge outline strokes for a binary region mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    edge_strokes: List[ContourPoints] = []
    for cnt in contours:
        if len(cnt) < 3:
            continue
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        pts = [(int(p[0][0]), int(p[0][1])) for p in approx]
        if len(pts) >= 3:
            pts.append(pts[0])  # Close contour loop
            edge_strokes.append(pts)
    return edge_strokes


def sort_layers_by_area(layers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort layers so that largest-area layers are painted first (background first)."""
    return sorted(layers, key=lambda l: l.get("area", 0), reverse=True)


def generate_full_painting_layers(
    image_path: str,
    num_colors: int = 12,
    fill_step: int = 2,
    min_region_area: int = 20,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]], Optional[np.ndarray]]:
    """
    Generates full multi-color painting reconstruction layers.
    
    Pipeline:
    1. K-Means quantize image into num_colors dominant colors
    2. For each color (largest area first, skip near-white):
       - Generate dense horizontal fill strokes (step=2px for full coverage)
       - Generate edge outline strokes for clean boundaries
    3. Preview is rendered as the quantized image itself (pixel-perfect reference)
    
    Returns: (layers, img_info, preview_canvas)
    """
    if not os.path.exists(image_path):
        return None, None, None

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        return None, None, None

    img_h, img_w, _ = image_bgr.shape
    img_info = {
        "height": img_h,
        "width": img_w,
        "center_x": img_w / 2.0,
        "center_y": img_h / 2.0,
    }

    # Slight bilateral filter to smooth noise before quantization
    smoothed = cv2.bilateralFilter(image_bgr, 9, 50, 50)

    quantized_bgr, palette_rgb, labels_2d, _ = quantize_colors_kmeans(smoothed, num_colors)

    preview_canvas = quantized_bgr.copy()
    layers: List[Dict[str, Any]] = []

    for k in range(num_colors):
        rgb_color = palette_rgb[k]

        # Skip near-white colors (Instagram canvas is already white)
        if is_near_white(rgb_color):
            continue

        mask = (labels_2d == k).astype(np.uint8) * 255

        # Remove tiny regions that would be noise
        num_labels, labels_im, stats, _ = cv2.connectedComponentsWithStats(mask)
        filtered_mask = np.zeros_like(mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_region_area:
                filtered_mask[labels_im == i] = 255

        pixel_count = int(np.count_nonzero(filtered_mask))
        if pixel_count == 0:
            continue

        # Generate dense fill strokes
        fill_strokes = generate_fill_strokes_for_mask(filtered_mask, step=fill_step)

        # Generate edge boundary strokes
        edge_strokes = generate_edge_strokes_for_mask(filtered_mask, epsilon=1.2)

        all_strokes = fill_strokes + edge_strokes

        layers.append({
            "name": f"Color RGB({rgb_color[0]},{rgb_color[1]},{rgb_color[2]})",
            "rgb": rgb_color,
            "area": pixel_count,
            "contours": all_strokes,
        })

    # Sort layers: paint largest areas first (background colors), smallest last (details)
    layers = sort_layers_by_area(layers)

    return layers, img_info, preview_canvas
