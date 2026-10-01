"""
Image Processor Facade Module.

Re-exports contour extraction, color matching, path optimization,
and palette definitions from modular src.vision and src.core packages.
"""

try:
    from src.core.constants import INSTAGRAM_DEFAULT_PALETTE
    from src.core.models import PaletteItem
    from src.vision import (
        color_distance_lab,
        extract_raw_contours,
        generate_sketch_contours,
        rgb_to_lab,
        sample_contour_color,
        simplify_contour,
        sort_contours_greedy,
    )
except (ImportError, ModuleNotFoundError):
    from core.constants import INSTAGRAM_DEFAULT_PALETTE  # type: ignore
    from core.models import PaletteItem  # type: ignore
    from vision import (  # type: ignore
        color_distance_lab,
        extract_raw_contours,
        generate_sketch_contours,
        rgb_to_lab,
        sample_contour_color,
        simplify_contour,
        sort_contours_greedy,
    )

__all__ = [
    "PaletteItem",
    "INSTAGRAM_DEFAULT_PALETTE",
    "rgb_to_lab",
    "color_distance_lab",
    "sample_contour_color",
    "sort_contours_greedy",
    "simplify_contour",
    "extract_raw_contours",
    "generate_sketch_contours",
]