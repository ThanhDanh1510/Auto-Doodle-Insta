"""
Drawer Facade Module.

Re-exports automation drivers, spectrum navigators, and FastDrawer
from the modular src.automation package for backward compatibility.
"""

try:
    from src.automation import (
        IS_WINDOWS,
        FastDrawer,
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
        gray_spectrum_pct,
        rainbow_spectrum_pct,
        smooth_drag_line,
        warm_spectrum_pct,
        win32_move,
        win32_press,
        win32_release,
    )
except (ImportError, ModuleNotFoundError):
    from automation import (  # type: ignore
        IS_WINDOWS,
        FastDrawer,
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
        gray_spectrum_pct,
        rainbow_spectrum_pct,
        smooth_drag_line,
        warm_spectrum_pct,
        win32_move,
        win32_press,
        win32_release,
    )

__all__ = [
    "FastDrawer",
    "IS_WINDOWS",
    "auto_detect_spectrum_page",
    "choose_best_page_for_color",
    "get_spectrum_position",
    "gray_spectrum_pct",
    "rainbow_spectrum_pct",
    "smooth_drag_line",
    "warm_spectrum_pct",
    "win32_move",
    "win32_press",
    "win32_release",
]
