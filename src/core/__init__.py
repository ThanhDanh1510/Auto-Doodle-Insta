"""
Core data structures, constants, and type definitions for AutoDoodle.
"""

try:
    from src.core.constants import INSTAGRAM_DEFAULT_PALETTE, SpectrumPage
    from src.core.models import (
        ColorGroup,
        ContourPoints,
        ImageInfo,
        LayerInfo,
        PaletteItem,
        Point2D,
        ProcessStats,
        RGBColor,
    )
except (ImportError, ModuleNotFoundError):
    from .constants import INSTAGRAM_DEFAULT_PALETTE, SpectrumPage  # type: ignore
    from .models import (  # type: ignore
        ColorGroup,
        ContourPoints,
        ImageInfo,
        LayerInfo,
        PaletteItem,
        Point2D,
        ProcessStats,
        RGBColor,
    )

__all__ = [
    "SpectrumPage",
    "INSTAGRAM_DEFAULT_PALETTE",
    "Point2D",
    "ContourPoints",
    "RGBColor",
    "PaletteItem",
    "ColorGroup",
    "LayerInfo",
    "ImageInfo",
    "ProcessStats",
]
