"""
Hardware low-level mouse driver using Windows Direct user32.mouse_event API with PyAutoGUI fallback.
"""

import sys
import time
import math
import pyautogui

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

    def win32_move(x: int, y: int) -> None:
        """Moves mouse pointer using Windows Direct API with 65535 normalized absolute coordinates."""
        nx = int(x * 65535 / SCREEN_W)
        ny = int(y * 65535 / SCREEN_H)
        user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)

    def win32_press() -> None:
        """Presses down left mouse button instantly via Win32."""
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def win32_release() -> None:
        """Releases left mouse button instantly via Win32."""
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
else:
    def win32_move(x: int, y: int) -> None:
        pyautogui.moveTo(x, y)

    def win32_press() -> None:
        pyautogui.mouseDown()

    def win32_release() -> None:
        pyautogui.mouseUp()


def smooth_drag_line(
    curr_x: int,
    curr_y: int,
    target_x: int,
    target_y: int,
    step_size: float = 2.0,
    step_delay: float = 0.002,
    fast_mode: bool = True
) -> None:
    """
    Interpolates mouse motion from (curr_x, curr_y) to (target_x, target_y)
    with step_size distance increments and sub-millisecond delays.
    """
    dx = target_x - curr_x
    dy = target_y - curr_y
    dist = math.hypot(dx, dy)
    delay = max(0.001, step_delay)
    use_fast = fast_mode and IS_WINDOWS

    if dist > step_size:
        steps = int(dist / step_size)
        for s in range(1, steps + 1):
            ix = int(curr_x + (dx * s / steps))
            iy = int(curr_y + (dy * s / steps))
            if use_fast:
                win32_move(ix, iy)
            else:
                pyautogui.moveTo(ix, iy)
            time.sleep(delay)
    else:
        if use_fast:
            win32_move(target_x, target_y)
        else:
            pyautogui.moveTo(target_x, target_y)
        time.sleep(delay)
