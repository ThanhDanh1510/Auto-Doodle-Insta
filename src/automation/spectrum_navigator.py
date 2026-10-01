"""
Instagram Spectrum Color Picker Navigator.

Calculates relative (x_pct, y_pct) coordinates for selecting specific RGB colors
on Instagram Stories' 3-page gradient color spectrum popover.
"""

from __future__ import annotations
import colorsys
from typing import Sequence, Dict, Any, Tuple


def rainbow_spectrum_pct(rgb: Sequence[int] | Tuple[int, int, int]) -> Tuple[float, float]:
    """
    Maps RGB to (x_pct, y_pct) on Page 1 (Rainbow) spectrum.
    
    9 Swatch Positions (spacing = 0.125):
      x=0.000: #1 Black / Dark Brown
      x=0.125: #2 Blue
      x=0.250: #3 Green
      x=0.375: #4 Yellow
      x=0.500: #5 Orange
      x=0.625: #6 Coral
      x=0.750: #7 Magenta
      x=0.875: #8 Purple
      x=1.000: #9 Red
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0

    # 1. Moss Green Stamen (Hue 25-85°, G > B, R < 130) -> Shift right to (x=0.295, y=0.15) for warm Moss Green
    if 25 <= hue <= 85 and r < 130 and g > b:
        return (0.295, 0.15)

    # 2. Dark Crimson / Red Wine tips & spots (V < 0.40, low brightness) -> Swatch 9 Red lower dark zone (x=0.960, y=0.20)
    if v < 0.40 and s > 0.30:
        return (0.960, 0.20)

    # Grayscale
    if s < 0.10:
        luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        return (0.020, 0.10 + luma * 0.40)

    # Piecewise hue-to-x mapping
    if hue >= 330:
        t = (hue - 330.0) / 40.0
        x_pct = 0.750 - t * 0.125
    elif hue < 10:
        t = (30.0 + hue) / 40.0
        x_pct = 0.750 - t * 0.125
    elif hue < 30:
        t = (hue - 10.0) / 20.0
        x_pct = 0.625 - t * 0.125
    elif hue < 60:
        t = (hue - 30.0) / 30.0
        x_pct = 0.500 - t * 0.125
    elif hue < 120:
        t = (hue - 60.0) / 60.0
        x_pct = 0.375 - t * 0.125
    elif hue <= 240:
        t = (hue - 120.0) / 120.0
        x_pct = 0.250 - t * 0.125
    elif hue < 280:
        x_pct = 0.125 if hue < 260 else 0.875
    else:
        t = (hue - 280.0) / 50.0
        x_pct = 0.875 - t * 0.125

    # Y-axis (Upward Popover Height)
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    y_pct = 0.30 + luma * 0.45

    return (max(0.0, min(1.0, x_pct)), max(0.05, min(0.95, y_pct)))


def warm_spectrum_pct(rgb: Sequence[int] | Tuple[int, int, int]) -> Tuple[float, float]:
    """
    Maps RGB to (x_pct, y_pct) on Page 2 (Warm/Skin) spectrum.
    Target: Soft Dusty Pastel Pink, Mauve, and Nude tones.
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # 1. Moss Green Stamen -> Shift right to (x = 0.295, y = 0.15) for warm Moss Green
    if 25 <= hue <= 85 and r < 130 and g > b:
        return (0.295, 0.15)

    # 2. Dark Crimson / Red Wine tips & spots -> Swatch 9 Red lower dark zone (x = 0.960, y = 0.20)
    if v < 0.40 and s > 0.30:
        return (0.960, 0.20)

    # Grayscale
    if s < 0.08:
        return (0.875 if v < 0.40 else 1.000, 0.10 + luma * 0.40)

    # X-axis: Map Pink/Red/Peach hues strictly to Swatch 1, 2, 3 (x = 0.0 to 0.25)
    if hue >= 300 or hue <= 15:
        if s > 0.45:
            # Saturated pink -> Swatch 1 Dusty Rose (x = 0.0)
            x_pct = 0.02 + (hue - 300) / 60.0 * 0.08 if hue >= 300 else 0.02
        else:
            # Pale Pink -> Swatch 2 Pale Pink (x = 0.125)
            x_pct = 0.125
    elif hue <= 40:
        # Cream Beige / Peach -> Swatch 3 (x = 0.250) or Swatch 4 (x = 0.375)
        x_pct = 0.250 if s < 0.25 else 0.375
    else:
        x_pct = 0.500

    # Y-axis: Drag HIGH UP into popover (y = 0.45 to 0.75) for soft pastel tones
    y_pct = 0.30 + luma * 0.55

    return (max(0.0, min(1.0, x_pct)), max(0.05, min(0.95, y_pct)))


def gray_spectrum_pct(rgb: Sequence[int] | Tuple[int, int, int]) -> Tuple[float, float]:
    """Page 3 (Gray): Simple brightness gradient."""
    r, g, b = rgb[0], rgb[1], rgb[2]
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    x_pct = 1.0 - luma
    return (max(0.0, min(1.0, x_pct)), 0.50)


def get_spectrum_position(rgb: Sequence[int] | Tuple[int, int, int], page: int = 1) -> Tuple[float, float]:
    """Returns normalized (x_pct, y_pct) on the specified spectrum page."""
    if page == 1:
        return rainbow_spectrum_pct(rgb)
    elif page == 3:
        return gray_spectrum_pct(rgb)
    else:
        return warm_spectrum_pct(rgb)


def choose_best_page_for_color(rgb: Sequence[int] | Tuple[int, int, int]) -> int:
    """
    Per-layer color page classifier for Hybrid Mode:
    - Page 2 (Warm): Soft Muted Dusty Pink, Mauve, Beige, Nude (S <= 0.65, V >= 0.40)
    - Page 1 (Rainbow): Deep Crimson, Dark Maroon spots, Olive Green stamen (S > 0.65 or V < 0.40)
    - Page 3 (Gray): Monochromatic low saturation (S < 0.08)
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue_deg = h * 360.0

    if s < 0.08:
        return 3  # Gray page for pure monochrome

    if hue_deg >= 290 or hue_deg <= 40:
        if s <= 0.65 and v >= 0.40:
            return 2  # Warm page (Muted Pastel Pink/Mauve)
        else:
            return 1  # Deep Crimson / Dark Maroon -> Page 1
    return 1


def auto_detect_spectrum_page(color_groups: Sequence[Dict[str, Any]]) -> int:
    """
    Analyzes full image palette to select best single page if Auto Mode (0) is selected.
    """
    vivid_count = 0
    soft_count = 0
    gray_count = 0

    for g in color_groups:
        page = choose_best_page_for_color(g["rgb"])
        if page == 1:
            vivid_count += 1
        elif page == 2:
            soft_count += 1
        else:
            gray_count += 1

    if vivid_count > 0:
        return 1
    elif soft_count > 0:
        return 2
    else:
        return 3
