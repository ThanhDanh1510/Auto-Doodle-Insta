"""
Automation Subpackage for AutoDoodle.

Provides OS-level mouse control, Instagram spectrum color picker navigation,
and stroke path execution.
"""

try:
    from src.automation.input_driver import (
        IS_WINDOWS,
        smooth_drag_line,
        win32_move,
        win32_press,
        win32_release,
    )
    from src.automation.spectrum_navigator import (
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
        gray_spectrum_pct,
        rainbow_spectrum_pct,
        warm_spectrum_pct,
    )
    from src.automation.stroke_executor import FastDrawer
except (ImportError, ModuleNotFoundError):
    from .input_driver import (  # type: ignore
        IS_WINDOWS,
        smooth_drag_line,
        win32_move,
        win32_press,
        win32_release,
    )
    from .spectrum_navigator import (  # type: ignore
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
        gray_spectrum_pct,
        rainbow_spectrum_pct,
        warm_spectrum_pct,
    )
    from .stroke_executor import FastDrawer  # type: ignore

__all__ = [
    "IS_WINDOWS",
    "win32_move",
    "win32_press",
    "win32_release",
    "smooth_drag_line",
    "rainbow_spectrum_pct",
    "warm_spectrum_pct",
    "gray_spectrum_pct",
    "get_spectrum_position",
    "choose_best_page_for_color",
    "auto_detect_spectrum_page",
    "FastDrawer",
]
