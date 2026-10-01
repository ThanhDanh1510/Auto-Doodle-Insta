"""
Painter Engine Facade Module.

Re-exports full multi-color painting generation, K-Means quantization,
and mask stroke generation from the modular src.vision package.
"""

try:
    from src.vision import (
        generate_edge_strokes_for_mask,
        generate_fill_strokes_for_mask,
        generate_full_painting_layers,
        is_near_white,
        quantize_colors_kmeans,
        sort_layers_by_area,
    )
except (ImportError, ModuleNotFoundError):
    from vision import (  # type: ignore
        generate_edge_strokes_for_mask,
        generate_fill_strokes_for_mask,
        generate_full_painting_layers,
        is_near_white,
        quantize_colors_kmeans,
        sort_layers_by_area,
    )

__all__ = [
    "quantize_colors_kmeans",
    "is_near_white",
    "generate_fill_strokes_for_mask",
    "generate_edge_strokes_for_mask",
    "sort_layers_by_area",
    "generate_full_painting_layers",
]
