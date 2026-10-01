"""
Stroke execution and hardware-accelerated drawing automation.

Executes calibrated contour paths on screen using fast Windows Win32 API
or cross-platform PyAutoGUI fallbacks, complete with spectrum color picking.
"""

from __future__ import annotations
import math
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import keyboard
import pyautogui

try:
    from src.automation.input_driver import (
        IS_WINDOWS,
        win32_move,
        win32_press,
        win32_release,
    )
    from src.automation.spectrum_navigator import (
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
    )
except (ImportError, ModuleNotFoundError):
    from automation.input_driver import (  # type: ignore
        IS_WINDOWS,
        win32_move,
        win32_press,
        win32_release,
    )
    from automation.spectrum_navigator import (  # type: ignore
        auto_detect_spectrum_page,
        choose_best_page_for_color,
        get_spectrum_position,
    )


class FastDrawer:
    """Automates mouse strokes and color selection for Instagram Story drawing canvas."""

    def __init__(
        self,
        pause_key: str = "space",
        stop_key: str = "q",
        fast_mode: bool = True,
        step_size: float = 2.0,
        point_delay: float = 0.002,
        spectrum_page: int = 4,
    ) -> None:
        self.pause_key = pause_key
        self.stop_key = stop_key
        self.fast_mode = fast_mode and IS_WINDOWS
        self.step_size = step_size
        self.point_delay = point_delay
        self.spectrum_page = spectrum_page
        self.current_page = 1  # Instagram starts on Page 1 (Rainbow) by default
        self.is_paused = False
        self.is_stopped = False
        self.effective_page = 1

    def check_stop_and_pause(self, status_callback: Optional[Callable[[str], None]] = None) -> None:
        """Polls emergency stop and pause hotkeys."""
        if keyboard.is_pressed(self.stop_key):
            self.is_stopped = True
            raise KeyboardInterrupt("Stop key pressed.")
        while self.is_paused:
            if keyboard.is_pressed(self.stop_key):
                self.is_stopped = True
                raise KeyboardInterrupt("Stop key pressed during pause.")
            if status_callback:
                status_callback("PAUSED. Press PAUSE key to resume...")
            time.sleep(0.1)

    def swipe_spectrum_page(
        self,
        spectrum_info: Sequence[Union[int, float]],
        from_page: int,
        to_page: int,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Swipes horizontally across swatch bar to change Instagram Spectrum Page."""
        spec_x1 = spectrum_info[0]
        spec_w = spectrum_info[2]
        if len(spectrum_info) >= 6:
            swatch_y = int(spectrum_info[5])
        elif len(spectrum_info) >= 5:
            swatch_y = int(spectrum_info[4])
        else:
            swatch_y = int(spectrum_info[1] + spectrum_info[3] * 0.5)

        page_diff = abs(to_page - from_page)

        for _ in range(page_diff):
            if from_page < to_page:
                start_x = int(spec_x1 + spec_w * 0.85)
                end_x = int(spec_x1 + spec_w * 0.15)
            else:
                start_x = int(spec_x1 + spec_w * 0.15)
                end_x = int(spec_x1 + spec_w * 0.85)

            if status_callback:
                status_callback(f"Swiping Spectrum Page ({from_page} → {to_page}) directly at swatch_y...")

            if self.fast_mode:
                win32_move(start_x, swatch_y)
                win32_press()
                steps = 10
                for i in range(1, steps + 1):
                    ix = int(start_x + (end_x - start_x) * (i / steps))
                    win32_move(ix, swatch_y)
                    time.sleep(0.002)
                win32_release()
            else:
                pyautogui.moveTo(start_x, swatch_y)
                pyautogui.dragTo(end_x, swatch_y, duration=0.08)

            time.sleep(0.3)

    def select_color_spectrum(
        self,
        spectrum_info: Sequence[Union[int, float]],
        target_rgb: Sequence[int] | Tuple[int, int, int],
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Navigates the Instagram spectrum color popup to pick target_rgb."""
        if len(spectrum_info) >= 6:
            x_left, y_upper, spec_w, popover_h, y_lower, swatch_y = spectrum_info[:6]
        elif len(spectrum_info) >= 5:
            x_left, y_upper, spec_w, popover_h, y_lower = spectrum_info[:5]
            swatch_y = y_lower + 15
        else:
            x_left, y_upper, spec_w, popover_h = spectrum_info[:4]
            y_lower = y_upper + popover_h
            swatch_y = y_lower + 15

        popover_height = max(10, int(y_lower - y_upper))

        if self.spectrum_page == 4:  # Hybrid Mode
            target_page = choose_best_page_for_color(target_rgb)
        elif self.spectrum_page == 0:  # Auto Mode
            target_page = getattr(self, "effective_page", 1)
        else:
            target_page = self.spectrum_page

        if self.current_page is not None and self.current_page != target_page:
            self.swipe_spectrum_page(spectrum_info, self.current_page, target_page, status_callback)
        self.current_page = target_page

        x_pct, y_pct = get_spectrum_position(target_rgb, target_page)
        target_x = int(x_left + spec_w * x_pct)

        y_clamped = max(0.05, min(0.95, y_pct))
        popover_y = int(y_lower - (y_clamped * popover_height))

        start_x = target_x
        start_y = int(swatch_y)

        page_names = {1: "Rainbow", 2: "Warm", 3: "Gray"}
        if status_callback:
            status_callback(
                f"[Page {target_page} ({page_names.get(target_page, '?')})] "
                f"RGB{tuple(target_rgb)} → X:{x_pct:.3f}, Y:{y_pct:.2f} → press({start_x},{start_y}) drag to ({target_x},{popover_y})"
            )

        # 1. Move to swatch circle
        if self.fast_mode:
            win32_move(start_x, start_y)
        else:
            pyautogui.moveTo(start_x, start_y)
        time.sleep(0.1)

        # 2. Press and HOLD for 1.2s to trigger Instagram spectrum popover expansion
        if self.fast_mode:
            win32_press()
        else:
            pyautogui.mouseDown()
        time.sleep(1.2)

        # 3. Smooth drag UPWARD into the popover gradient rectangle
        num_steps = 30
        for i in range(1, num_steps + 1):
            frac = i / num_steps
            iy = int(start_y + (popover_y - start_y) * frac)
            if self.fast_mode:
                win32_move(start_x, iy)
            else:
                pyautogui.moveTo(start_x, iy)
            time.sleep(0.015)

        # 4. Hold at target color for 0.5s to lock in color selection
        time.sleep(0.5)

        # 5. Release mouse
        if self.fast_mode:
            win32_release()
        else:
            pyautogui.mouseUp()
        time.sleep(0.35)

    def smooth_drag_to(
        self,
        curr_x: int,
        curr_y: int,
        target_x: int,
        target_y: int,
        step_delay: float = 0.002,
    ) -> None:
        """Smooth interpolated mouse drag between points."""
        dx = target_x - curr_x
        dy = target_y - curr_y
        dist = math.hypot(dx, dy)
        delay = max(0.001, step_delay)

        if dist > self.step_size:
            steps = int(dist / self.step_size)
            for s in range(1, steps + 1):
                ix = int(curr_x + (dx * s / steps))
                iy = int(curr_y + (dy * s / steps))
                if self.fast_mode:
                    win32_move(ix, iy)
                else:
                    pyautogui.moveTo(ix, iy)
                time.sleep(delay)
        else:
            if self.fast_mode:
                win32_move(target_x, target_y)
            else:
                pyautogui.moveTo(target_x, target_y)
            time.sleep(delay)

    def draw_color_groups(
        self,
        color_groups: Sequence[Dict[str, Any]],
        scale_factor: float,
        canvas_center_x: int,
        canvas_center_y: int,
        img_center_x: float,
        img_center_y: float,
        color_bar_info: Optional[Sequence[Union[int, float]]] = None,
        color_mode: str = "spectrum",
        point_delay: float = 0.002,
        stroke_delay: float = 0.01,
        progress_callback: Optional[Callable[[int, int, int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Draws all color layers and strokes onto the calibrated canvas."""
        self.is_paused = False
        self.is_stopped = False

        total_contours = sum(len(g["contours"]) for g in color_groups)
        if total_contours == 0:
            if status_callback:
                status_callback("No contours to draw.")
            return

        pyautogui.PAUSE = 0.0
        pyautogui.MINIMUM_DURATION = 0.0

        if color_bar_info:
            spectrum_info = color_bar_info
        else:
            spec_w = img_center_x * scale_factor * 2.0
            spec_h = 75.0
            spec_x1 = canvas_center_x - (spec_w / 2.0)
            spec_y1 = canvas_center_y + (img_center_y * scale_factor) + 15
            spectrum_info = (spec_x1, spec_y1, spec_w, spec_h)

        drawn_count = 0

        # Auto-detect spectrum page if set to 0 (Auto)
        effective_page = self.spectrum_page
        if effective_page == 0:
            effective_page = auto_detect_spectrum_page(color_groups)
            page_names = {1: "Rainbow (Cầu vồng)", 2: "Warm (Tông ấm)", 3: "Gray (Xám)"}
            if status_callback:
                status_callback(f"Auto-detected: Page {effective_page} - {page_names.get(effective_page, '')}")
        self.effective_page = effective_page
        self.current_page = 1  # Assume Instagram starts on Page 1 (Rainbow)

        try:
            for group_idx, group in enumerate(color_groups):
                self.check_stop_and_pause(status_callback)

                contours = group["contours"]
                color_rgb = group["rgb"]

                if not contours:
                    continue

                if status_callback:
                    status_callback(
                        f"Layer {group_idx+1}/{len(color_groups)}: RGB{tuple(color_rgb)} "
                        f"({len(contours)} strokes)"
                    )

                if color_mode in ["spectrum", "full_painting"]:
                    self.select_color_spectrum(spectrum_info, color_rgb, status_callback)

                for cnt in contours:
                    self.check_stop_and_pause(status_callback)
                    if len(cnt) < 2:
                        continue

                    drawn_count += 1
                    if progress_callback:
                        pct = int((drawn_count / total_contours) * 100)
                        progress_callback(drawn_count, total_contours, pct)

                    first_pt = cnt[0]
                    curr_x = int(canvas_center_x + (first_pt[0] - img_center_x) * scale_factor)
                    curr_y = int(canvas_center_y + (first_pt[1] - img_center_y) * scale_factor)

                    if self.fast_mode:
                        win32_move(curr_x, curr_y)
                        time.sleep(0.01)
                        win32_press()
                        time.sleep(0.015)
                    else:
                        pyautogui.moveTo(curr_x, curr_y)
                        pyautogui.mouseDown()
                        time.sleep(0.015)

                    for pt in cnt[1:]:
                        self.check_stop_and_pause(status_callback)
                        target_x = int(canvas_center_x + (pt[0] - img_center_x) * scale_factor)
                        target_y = int(canvas_center_y + (pt[1] - img_center_y) * scale_factor)
                        self.smooth_drag_to(curr_x, curr_y, target_x, target_y, step_delay=point_delay)
                        curr_x, curr_y = target_x, target_y

                    time.sleep(0.005)
                    if self.fast_mode:
                        win32_release()
                    else:
                        pyautogui.mouseUp()

                    if stroke_delay > 0:
                        time.sleep(stroke_delay)

            if status_callback:
                status_callback("Full Image Reconstruction completed!")

        except KeyboardInterrupt:
            if status_callback:
                status_callback(f"Drawing stopped by user ('{self.stop_key}').")
        except Exception as e:
            if status_callback:
                status_callback(f"Error during drawing: {e}")
        finally:
            if self.fast_mode:
                win32_release()
            else:
                pyautogui.mouseUp()
