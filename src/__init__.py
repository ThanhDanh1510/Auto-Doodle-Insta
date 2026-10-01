"""
AutoDoodle - Automated Instagram Story Canvas Painter and Sketch Engine.

Subpackages:
- src.core: Shared data structures, constants, and color palette definitions.
- src.vision: Edge detection, color quantization, contour simplification, greedy optimization, and region filling.
- src.automation: Win32/PyAutoGUI input drivers, spectrum color navigators, and FastDrawer execution engine.
"""

from src.automation import FastDrawer, win32_move, win32_press, win32_release
from src.core import INSTAGRAM_DEFAULT_PALETTE, SpectrumPage
from src.vision import (
    generate_full_painting_layers,
    generate_sketch_contours,
    quantize_colors_kmeans,
    simplify_contour,
    sort_contours_greedy,
)

__all__ = [
    "INSTAGRAM_DEFAULT_PALETTE",
    "SpectrumPage",
    "FastDrawer",
    "win32_move",
    "win32_press",
    "win32_release",
    "quantize_colors_kmeans",
    "simplify_contour",
    "sort_contours_greedy",
    "generate_sketch_contours",
    "generate_full_painting_layers",
]
