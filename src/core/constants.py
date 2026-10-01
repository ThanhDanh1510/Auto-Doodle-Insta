"""
Global constants and palette definitions for AutoDoodle.
"""

from typing import List
from .models import PaletteItem
from enum import IntEnum


class SpectrumPage(IntEnum):
    AUTO = 0
    RAINBOW = 1
    WARM = 2
    GRAY = 3
    HYBRID = 4


INSTAGRAM_DEFAULT_PALETTE: List[PaletteItem] = [
    {"name": "Đen (Black)", "rgb": (0, 0, 0), "pct": 0.05},
    {"name": "Xanh dương (Blue)", "rgb": (0, 149, 246), "pct": 0.16},
    {"name": "Xanh lá (Green)", "rgb": (9, 187, 95), "pct": 0.28},
    {"name": "Vàng (Yellow)", "rgb": (255, 204, 0), "pct": 0.39},
    {"name": "Cam (Orange)", "rgb": (255, 149, 0), "pct": 0.50},
    {"name": "Đỏ san hô (Coral)", "rgb": (255, 59, 48), "pct": 0.61},
    {"name": "Hồng đậm (Magenta)", "rgb": (255, 45, 85), "pct": 0.72},
    {"name": "Tím (Purple)", "rgb": (175, 82, 222), "pct": 0.84},
    {"name": "Đỏ (Red)", "rgb": (255, 0, 0), "pct": 0.95},
]
