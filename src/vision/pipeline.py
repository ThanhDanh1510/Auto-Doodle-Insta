"""
High-level image processing and contour generation pipeline.
"""

from __future__ import annotations
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np
from colorama import Fore

try:
    from src.core.constants import INSTAGRAM_DEFAULT_PALETTE
    from src.core.models import ImageInfo, ProcessStats
    from src.vision.color_matcher import color_distance_lab, sample_contour_color
    from src.vision.edge_detector import extract_raw_contours
    from src.vision.fill_engine import generate_full_painting_layers
    from src.vision.optimizer import sort_contours_greedy
    from src.vision.simplifier import simplify_contour
except (ImportError, ModuleNotFoundError):
    from core.constants import INSTAGRAM_DEFAULT_PALETTE  # type: ignore
    from core.models import ImageInfo, ProcessStats  # type: ignore
    from vision.color_matcher import color_distance_lab, sample_contour_color  # type: ignore
    from vision.edge_detector import extract_raw_contours  # type: ignore
    from vision.fill_engine import generate_full_painting_layers  # type: ignore
    from vision.optimizer import sort_contours_greedy  # type: ignore
    from vision.simplifier import simplify_contour  # type: ignore


def generate_sketch_contours(
    image_path: str,
    mode: str = "canny",
    canny_lower: int = 50,
    canny_upper: int = 150,
    blur_kernel: int = 5,
    epsilon: float = 1.0,
    min_length: int = 4,
    optimize_path: bool = True,
    color_mode: str = "monochrome",  # "monochrome", "palette", "spectrum", "full_painting"
    num_painting_colors: int = 8,
    status_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[
    Optional[List[Dict[str, Any]]],
    Optional[ImageInfo],
    Optional[np.ndarray],
    Optional[ProcessStats],
]:
    """
    Processes an input image and extracts sketch contours or full-color reconstruction layers.
    :return: (color_groups, img_info, preview_canvas, stats)
    """

    def log_status(msg: str) -> None:
        print(msg)
        if status_callback:
            status_callback(msg)

    if not os.path.exists(image_path):
        log_status(f"{Fore.RED}Error: Image file '{image_path}' not found.")
        return None, None, None, None

    # Full Painting Reconstruction Engine Mode
    if color_mode == "full_painting":
        log_status(f"{Fore.CYAN}Generating Full-Color Painting ({num_painting_colors} colors)...")
        layers, img_info, preview_canvas = generate_full_painting_layers(
            image_path, num_colors=num_painting_colors, fill_step=2
        )
        if layers is None or img_info is None or preview_canvas is None:
            log_status(f"{Fore.RED}Error: Full painting generation failed.")
            return None, None, None, None

        total_contours = sum(len(g["contours"]) for g in layers)
        total_points = sum(sum(len(c) for c in g["contours"]) for g in layers)

        stats: ProcessStats = {
            "total_contours": total_contours,
            "color_groups_count": len(layers),
            "original_points": total_points,
            "simplified_points": total_points,
            "reduction_percent": 0.0,
        }
        log_status(f"{Fore.GREEN}Full painting ready: {len(layers)} color layers, {total_contours} strokes.")
        return layers, img_info, preview_canvas, stats

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        log_status(f"{Fore.RED}Error: Could not read image '{image_path}'.")
        return None, None, None, None

    img_height, img_width, _ = image_bgr.shape
    img_info: ImageInfo = {
        "height": img_height,
        "width": img_width,
        "center_x": img_width / 2.0,
        "center_y": img_height / 2.0,
    }

    raw_contours, original_point_count = extract_raw_contours(
        image_bgr,
        mode=mode,
        canny_lower=canny_lower,
        canny_upper=canny_upper,
        blur_kernel=blur_kernel,
    )

    preview_canvas = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255
    color_groups: List[Dict[str, Any]] = []

    if color_mode == "monochrome":
        mono_contours = []
        for cnt in raw_contours:
            simplified = simplify_contour(cnt, epsilon)
            if len(simplified) >= min_length:
                mono_contours.append(simplified)
        if optimize_path and mono_contours:
            mono_contours = sort_contours_greedy(mono_contours)

        for cnt in mono_contours:
            if len(cnt) > 1:
                pts = np.array(cnt, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(preview_canvas, [pts], isClosed=False, color=(0, 0, 0), thickness=1)

        color_groups.append({
            "name": "Black",
            "rgb": (0, 0, 0),
            "pct": 0.15,
            "contours": mono_contours,
        })
    else:
        swatch_groups: Dict[int, List[Tuple[List[Tuple[int, int]], Tuple[int, int, int]]]] = {
            i: [] for i in range(len(INSTAGRAM_DEFAULT_PALETTE))
        }

        for cnt in raw_contours:
            simplified = simplify_contour(cnt, epsilon)
            if len(simplified) < min_length:
                continue

            sampled_rgb = sample_contour_color(image_bgr, simplified)
            best_idx = min(
                range(len(INSTAGRAM_DEFAULT_PALETTE)),
                key=lambda idx: color_distance_lab(sampled_rgb, INSTAGRAM_DEFAULT_PALETTE[idx]["rgb"]),
            )
            target_color = sampled_rgb if color_mode == "spectrum" else INSTAGRAM_DEFAULT_PALETTE[best_idx]["rgb"]
            swatch_groups[best_idx].append((simplified, target_color))

        for idx, items in swatch_groups.items():
            if not items:
                continue
            swatch_info = INSTAGRAM_DEFAULT_PALETTE[idx]
            group_contours = [item[0] for item in items]
            if optimize_path:
                group_contours = sort_contours_greedy(group_contours)

            rgb_val = swatch_info["rgb"]
            bgr_color = (rgb_val[2], rgb_val[1], rgb_val[0])
            for cnt in group_contours:
                if len(cnt) > 1:
                    pts = np.array(cnt, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(preview_canvas, [pts], isClosed=False, color=bgr_color, thickness=1)

            color_groups.append({
                "name": swatch_info["name"],
                "rgb": swatch_info["rgb"],
                "pct": swatch_info["pct"],
                "contours": group_contours,
            })

    total_contours = sum(len(g["contours"]) for g in color_groups)
    simplified_point_count = sum(sum(len(c) for c in g["contours"]) for g in color_groups)
    reduction = 0.0
    if original_point_count > 0:
        reduction = (1.0 - (simplified_point_count / original_point_count)) * 100.0

    stats: ProcessStats = {
        "total_contours": total_contours,
        "color_groups_count": len(color_groups),
        "original_points": original_point_count,
        "simplified_points": simplified_point_count,
        "reduction_percent": round(reduction, 1),
    }

    log_status(
        f"{Fore.GREEN}Processed image: {total_contours} contours in {len(color_groups)} colors, "
        f"{simplified_point_count} points."
    )

    return color_groups, img_info, preview_canvas, stats
