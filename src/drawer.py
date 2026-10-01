import time
import sys
import math
import colorsys
import pyautogui
import keyboard

IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    import ctypes
    user32 = ctypes.windll.user32

    SCREEN_W = user32.GetSystemMetrics(0)
    SCREEN_H = user32.GetSystemMetrics(1)

    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_ABSOLUTE = 0x8000

    def win32_move(x, y):
        nx = int(x * 65535 / SCREEN_W)
        ny = int(y * 65535 / SCREEN_H)
        user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)

    def win32_press():
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def win32_release():
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
else:
    def win32_move(x, y):
        pyautogui.moveTo(x, y)

    def win32_press():
        pyautogui.mouseDown()

    def win32_release():
        pyautogui.mouseUp()


# ============================================================
# Instagram Spectrum Color Picker - Confirmed Swatch Layout
# ============================================================
#
# CALIBRATION: User calibrates 5 corners using Key 'E'
#
# PAGE 1 (Rainbow) Swatch Positions (9 swatches, spacing = 0.125):
#   x=0.000: #1 Đen (Black)
#   x=0.125: #2 Xanh dương (Blue)
#   x=0.250: #3 Xanh lá (Green)      ← STAMEN OLIVE GREEN HERE (x=0.25, y=0.35)
#   x=0.375: #4 Vàng (Yellow)
#   x=0.500: #5 Cam (Orange)
#   x=0.625: #6 Đỏ san hồ (Coral)
#   x=0.750: #7 Hồng đậm (Magenta)   ← DEEP PINK / LILY ACCENTS
#   x=0.875: #8 Tím (Purple)
#   x=1.000: #9 Đỏ (Red)
#
# PAGE 2 (Warm) Swatch Positions (9 swatches, spacing = 0.125):
#   x=0.000: #1 Hồng đất (Dusty Rose)     ← PETALS SOFT DUSTY PINK (x=0.02-0.12, y=0.50-0.70)
#   x=0.125: #2 Hồng phấn (Pale Pink)
#   x=0.250: #3 Beige nhạt (Cream Beige)
#   x=0.375: #4 Cam đào (Peach)
#   x=0.500: #5 Nâu sáng (Ochre)          ← STAMEN OLIVE GREEN HERE (x=0.50, y=0.35)
#   x=0.625: #6 Nâu đất (Dark Brown)
#   x=0.750: #7 Đen xám (Off-black)       ← DARK MAROON SPOTS (x=0.75, y=0.15)
#   x=0.875: #8 Xám thẫm (Dark Gray)
#   x=1.000: #9 Xám vừa (Medium Gray)
# ============================================================


def rainbow_spectrum_pct(rgb):
    """
    Maps RGB to (x_pct, y_pct) on Page 1 (Rainbow) spectrum.
    
    9 Swatch Positions (spacing = 0.125):
      x=0.000: #1 Đen (Black / Dark Brown)  ← DARK MAROON TIPS HERE (x=0.02, y=0.15)
      x=0.125: #2 Xanh dương (Blue)
      x=0.250: #3 Xanh lá (Green)           ← STAMEN OLIVE GREEN HERE (x=0.25, y=0.35)
      x=0.375: #4 Vàng (Yellow)
      x=0.500: #5 Cam (Orange)
      x=0.625: #6 Đỏ san hồ (Coral)
      x=0.750: #7 Hồng đậm (Magenta)
      x=0.875: #8 Tím (Purple)
      x=1.000: #9 Đỏ (Red)
    """
    r, g, b = rgb
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

    # === Piecewise hue-to-x mapping ===
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


def warm_spectrum_pct(rgb):
    """
    Maps RGB to (x_pct, y_pct) on Page 2 (Warm/Skin) spectrum.
    Target: Soft Dusty Pastel Pink, Mauve, and Nude tones matching preview!
    - Swatch 1 & 2 High Drag (x = 0.02 to 0.12, y = 0.50 to 0.75) = Soft Dusty Pink / Mauve / Beige!
    """
    r, g, b = rgb
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

    # Y-axis: Drag HIGH UP into popover (y = 0.45 to 0.75) for SOFT DUSTY PASTEL PINK!
    y_pct = 0.30 + luma * 0.55

    return (max(0.0, min(1.0, x_pct)), max(0.05, min(0.95, y_pct)))


def gray_spectrum_pct(rgb):
    """Page 3 (Gray): Simple brightness gradient."""
    r, g, b = rgb
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    x_pct = 1.0 - luma
    return (max(0.0, min(1.0, x_pct)), 0.50)


def get_spectrum_position(rgb, page=1):
    if page == 1:
        return rainbow_spectrum_pct(rgb)
    elif page == 3:
        return gray_spectrum_pct(rgb)
    else:
        return warm_spectrum_pct(rgb)


def auto_detect_spectrum_page(color_groups):
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


def choose_best_page_for_color(rgb):
    """
    Per-layer color page classifier for Hybrid Mode:
    - Page 2 (Warm): Soft Muted Dusty Pink, Mauve, Beige, Nude (S <= 0.65, V >= 0.40)
      Guarantees all soft petal shading layers use Instagram Page 2 Warm Spectrum!
    - Page 1 (Rainbow): Deep Crimson, Dark Maroon spots, Olive Green stamen (S > 0.65 or V < 0.40)
      Provides rich deep outlines, dark spots, and green stamen.
    """
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue_deg = h * 360.0

    if s < 0.08:
        return 3  # Gray page for pure monochrome

    if (hue_deg >= 290 or hue_deg <= 40):
        if s <= 0.65 and v >= 0.40:
            return 2  # Warm page (Muted Pastel Pink/Mauve)
        else:
            return 1  # Deep Crimson / Dark Maroon -> Page 1
    return 1


class FastDrawer:
    def __init__(self, pause_key="space", stop_key="q", fast_mode=True,
                 step_size=2.0, point_delay=0.002, spectrum_page=4):
        self.pause_key = pause_key
        self.stop_key = stop_key
        self.fast_mode = fast_mode and IS_WINDOWS
        self.step_size = step_size
        self.point_delay = point_delay
        self.spectrum_page = spectrum_page
        self.current_page = 1  # Instagram starts on Page 1 (Rainbow) by default!
        self.is_paused = False
        self.is_stopped = False

    def check_stop_and_pause(self, status_callback=None):
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

    def swipe_spectrum_page(self, spectrum_info, from_page, to_page, status_callback=None):
        """Swipes horizontally across swatch bar to change Instagram Spectrum Page."""
        spec_x1 = spectrum_info[0]
        spec_w = spectrum_info[2]
        if len(spectrum_info) >= 6:
            swatch_y = int(spectrum_info[5])
        elif len(spectrum_info) >= 5:
            swatch_y = int(spectrum_info[4])
        else:
            swatch_y = int(spectrum_info[1] + spectrum_info[3] * 0.5)

        # Calculate swipe steps (page difference)
        page_diff = abs(to_page - from_page)

        for step in range(page_diff):
            if from_page < to_page:
                # Swipe left (drag right to left)
                start_x = int(spec_x1 + spec_w * 0.85)
                end_x = int(spec_x1 + spec_w * 0.15)
            else:
                # Swipe right (drag left to right)
                start_x = int(spec_x1 + spec_w * 0.15)
                end_x = int(spec_x1 + spec_w * 0.85)

            if status_callback:
                page_names = {1: "Rainbow", 2: "Warm", 3: "Gray"}
                status_callback(f"Swiping Spectrum Page ({from_page} → {to_page}) directly at swatch_y...")

            if self.fast_mode:
                win32_move(start_x, swatch_y)
                win32_press()
                # Fast drag transition
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

    def select_color_spectrum(self, spectrum_info, target_rgb, status_callback=None):
        if len(spectrum_info) >= 6:
            x_left, y_upper, spec_w, popover_h, y_lower, swatch_y = spectrum_info[:6]
        elif len(spectrum_info) >= 5:
            x_left, y_upper, spec_w, popover_h, y_lower = spectrum_info[:5]
            swatch_y = y_lower + 15
        else:
            x_left, y_upper, spec_w, popover_h = spectrum_info[:4]
            y_lower = y_upper + popover_h
            swatch_y = y_lower + 15

        popover_height = max(10, y_lower - y_upper)

        # Determine target page
        if self.spectrum_page == 4:  # Hybrid Mode
            target_page = choose_best_page_for_color(target_rgb)
        elif self.spectrum_page == 0:  # Auto Mode
            target_page = getattr(self, 'effective_page', 1)
        else:
            target_page = self.spectrum_page

        # Handle page swipe if changing pages in Hybrid mode
        if self.current_page is not None and self.current_page != target_page:
            self.swipe_spectrum_page(spectrum_info, self.current_page, target_page, status_callback)
        self.current_page = target_page

        x_pct, y_pct = get_spectrum_position(target_rgb, target_page)
        target_x = int(x_left + spec_w * x_pct)

        # Clamp y_pct between 0.05 and 0.95 to stay safely inside popover bounds
        y_clamped = max(0.05, min(0.95, y_pct))
        popover_y = int(y_lower - (y_clamped * popover_height))

        # Start press down directly at the target X on the swatch row (swatch_y)
        start_x = target_x
        start_y = int(swatch_y)

        page_names = {1: "Rainbow", 2: "Warm", 3: "Gray"}
        if status_callback:
            status_callback(
                f"[Page {target_page} ({page_names.get(target_page, '?')})] "
                f"RGB{target_rgb} → X:{x_pct:.3f}, Y:{y_pct:.2f} → press({start_x},{start_y}) drag to ({target_x},{popover_y})"
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

    def smooth_drag_to(self, curr_x, curr_y, target_x, target_y, step_delay=0.002):
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

    def draw_color_groups(self, color_groups, scale_factor, canvas_center_x, canvas_center_y,
                          img_center_x, img_center_y, color_bar_info=None, color_mode="spectrum",
                          point_delay=0.002, stroke_delay=0.01, progress_callback=None, status_callback=None):
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
            spec_w = (img_center_x * scale_factor * 2.0)
            spec_h = 75
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
                        f"Layer {group_idx+1}/{len(color_groups)}: RGB{color_rgb} "
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
