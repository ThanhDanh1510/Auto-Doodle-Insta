"""
Vision subpackage containing quantizers, edge detectors, path optimizers, fill engines, and pipelines.
"""

try:
    from src.vision.color_matcher import color_distance_lab, rgb_to_lab, sample_contour_color
    from src.vision.edge_detector import extract_raw_contours
    from src.vision.fill_engine import (
        generate_edge_strokes_for_mask,
        generate_fill_strokes_for_mask,
        generate_full_painting_layers,
        sort_layers_by_area,
    )
    from src.vision.optimizer import sort_contours_greedy
    from src.vision.pipeline import generate_sketch_contours
    from src.vision.quantizer import is_near_white, quantize_colors_kmeans
    from src.vision.simplifier import simplify_contour
except (ImportError, ModuleNotFoundError):
    from .color_matcher import color_distance_lab, rgb_to_lab, sample_contour_color  # type: ignore
    from .edge_detector import extract_raw_contours  # type: ignore
    from .fill_engine import (  # type: ignore
        generate_edge_strokes_for_mask,
        generate_fill_strokes_for_mask,
        generate_full_painting_layers,
        sort_layers_by_area,
    )
    from .optimizer import sort_contours_greedy  # type: ignore
    from .pipeline import generate_sketch_contours  # type: ignore
    from .quantizer import is_near_white, quantize_colors_kmeans  # type: ignore
    from .simplifier import simplify_contour  # type: ignore

__all__ = [
    "quantize_colors_kmeans",
    "is_near_white",
    "extract_raw_contours",
    "simplify_contour",
    "sort_contours_greedy",
    "rgb_to_lab",
    "color_distance_lab",
    "sample_contour_color",
    "generate_fill_strokes_for_mask",
    "generate_edge_strokes_for_mask",
    "sort_layers_by_area",
    "generate_full_painting_layers",
    "generate_sketch_contours",
]
