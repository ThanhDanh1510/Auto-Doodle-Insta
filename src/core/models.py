"""
Data models and typed structures for images, contours, and layers.
"""

from typing import TypedDict, Tuple, List, Dict, Any, Optional

Point2D = Tuple[int, int]
ContourPoints = List[Point2D]
RGBColor = Tuple[int, int, int]


class PaletteItem(TypedDict):
    name: str
    rgb: RGBColor
    pct: float


class ColorGroup(TypedDict):
    name: str
    rgb: RGBColor
    pct: float
    contours: List[ContourPoints]


class LayerInfo(TypedDict):
    name: str
    rgb: RGBColor
    area: int
    contours: List[ContourPoints]


class ImageInfo(TypedDict):
    height: int
    width: int
    center_x: float
    center_y: float


class ProcessStats(TypedDict):
    total_contours: int
    color_groups_count: int
    original_points: int
    simplified_points: int
    reduction_percent: float
