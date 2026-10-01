import os
import sys
import time
import json
import queue
import re
import threading
from typing import Optional, Tuple, List, Dict, Any

import cv2
import numpy as np
import pyautogui
import keyboard
import mouse
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from tkinter.constants import (
    BOTH, HORIZONTAL, LEFT, RIGHT, X, Y, SUNKEN,
    W, E, CENTER, DISABLED, NORMAL, WORD, END
)

# Ensure src and project root directory are on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import image_processor
from drawer import FastDrawer

config: Dict[str, Any] = {}
canvas_info: Optional[Tuple[int, int, int, int, float, float]] = None
color_bar_info: Optional[Tuple[int, int, int, int, int, int]] = None
selected_image_path: str = ""
current_color_groups: List[Dict[str, Any]] = []
current_img_info: Optional[Dict[str, Any]] = None
current_stats: Optional[Dict[str, Any]] = None
console_queue: queue.Queue = queue.Queue()


class QueueRedirector:
    """Redirects stdout/stderr to a thread-safe queue."""
    def __init__(self, q):
        self.queue = q
        self.ansi_escape = re.compile(r'\033\[[0-9;]*m')

    def write(self, text):
        cleaned = self.ansi_escape.sub('', text)
        if cleaned:
            self.queue.put(cleaned)

    def flush(self):
        pass


def load_config():
    global config, selected_image_path, color_bar_info
    config_file = 'config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            selected_image_path = config.get('default_image_path', 'assets/samples/Lily.png')
            if not os.path.exists(selected_image_path):
                if os.path.exists('assets/samples/Lily.png'):
                    selected_image_path = 'assets/samples/Lily.png'
                elif os.path.exists('images/Lily.png'):
                    selected_image_path = 'images/Lily.png'
            color_bar_info = config.get('color_bar_info', None)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    else:
        config = {
            "drawing_speed": 0.0,
            "stop_key": "q",
            "pause_key": "space",
            "ui_confidence": 0.8,
            "draw_button_y_offset": 75,
            "thickness_adjust_y_offset": 20,
            "scale_margin": 0.9,
            "plus_icons": ["assets/icons/plus_icon.png", "plus_icon.png"],
            "slider_handles": [
                "assets/icons/thickness_slider_handle.png",
                "assets/icons/thickness_slider_handle_alt.png",
                "thickness_slider_handle.png",
                "thickness_slider_handle_alt.png"
            ],
            "fast_drawing_mode": True,
            "color_mode": "full_painting",
            "num_painting_colors": 8,
            "epsilon": 0.3,
            "min_contour_length": 2,
            "canny_lower": 30,
            "canny_upper": 100,
            "blur_kernel": 3,
            "edge_mode": "canny",
            "optimize_path": True,
            "point_delay": 0.002,
            "stroke_delay": 0.01,
            "step_size": 2.0,
            "color_bar_info": None
        }


def save_config():
    try:
        config["color_bar_info"] = color_bar_info
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config.json: {e}")


def locate_robust(image_list):
    for image_file in image_list:
        if not os.path.exists(image_file):
            continue
        try:
            coords = pyautogui.locateCenterOnScreen(image_file, confidence=config.get('ui_confidence', 0.8))
            if coords:
                return coords
        except Exception:
            pass
    return None


class AutoDoodleApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("AutoDoodle Pro - Full Spectrum Painting Engine")
        self.root.geometry("960x810")
        self.root.minsize(850, 650)

        try:
            icon_candidates = [
                os.path.join("assets", "icons", "icon.ico"),
                "icon.ico"
            ]
            for icon_p in icon_candidates:
                if os.path.exists(icon_p):
                    self.root.iconbitmap(icon_p)
                    break
        except Exception:
            pass

        self.preview_image_tk = None
        self.preview_debounce_timer = None

        self._build_ui()
        self._update_preview()

    def _build_ui(self):
        main_paned = ttk.Panedwindow(self.root, orient=HORIZONTAL)
        main_paned.pack(fill=BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(left_frame, weight=1)

        right_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(right_frame, weight=1)

        # === LEFT PANEL ===
        # 1. Image Selection
        img_lf = ttk.Labelframe(left_frame, text="1. Image Selection", padding=10)
        img_lf.pack(fill=X, pady=(0, 10))

        btn_select = ttk.Button(img_lf, text="Browse Image...", command=self.select_image, bootstyle="info")
        btn_select.pack(side=LEFT, padx=(0, 10))

        self.lbl_image_name = ttk.Label(img_lf, text=os.path.basename(selected_image_path), relief=SUNKEN, padding=5)
        self.lbl_image_name.pack(side=LEFT, fill=X, expand=True)

        # 2. Masterpiece Mode & Presets
        preset_lf = ttk.Labelframe(left_frame, text="2. Reconstruction Mode & Presets", padding=10)
        preset_lf.pack(fill=X, pady=(0, 10))

        btn_p_full = ttk.Button(preset_lf, text="🎨 Full Painting (Tái tạo ảnh gốc)", command=self.apply_full_painting, bootstyle="success")
        btn_p_full.pack(side=LEFT, fill=X, expand=True, padx=2)

        btn_p_high = ttk.Button(preset_lf, text="🎯 Ultra Sketch (Paint Level)", command=self.apply_ultra_detail, bootstyle="danger")
        btn_p_high.pack(side=LEFT, fill=X, expand=True, padx=2)

        btn_p_bal = ttk.Button(preset_lf, text="🖊️ Outline", command=self.apply_clean_outline, bootstyle="secondary")
        btn_p_bal.pack(side=LEFT, fill=X, expand=True, padx=2)

        # 3. Fine Tuning Controls
        proc_lf = ttk.Labelframe(left_frame, text="3. Fine Controls & Color Quantization", padding=10)
        proc_lf.pack(fill=X, pady=(0, 10))

        # Drawing Mode
        color_mode_frame = ttk.Frame(proc_lf)
        color_mode_frame.pack(fill=X, pady=2)
        ttk.Label(color_mode_frame, text="Drawing Engine Mode:").pack(side=LEFT)
        self.combo_color_mode = ttk.Combobox(
            color_mode_frame, 
            values=["full_painting", "monochrome", "palette", "spectrum"], 
            state="readonly", 
            width=16
        )
        self.combo_color_mode.set(config.get("color_mode", "full_painting"))
        self.combo_color_mode.pack(side=RIGHT)
        self.combo_color_mode.bind("<<ComboboxSelected>>", lambda e: self.on_setting_changed())

        # Instagram Spectrum Page
        spec_page_frame = ttk.Frame(proc_lf)
        spec_page_frame.pack(fill=X, pady=2)
        ttk.Label(spec_page_frame, text="Instagram Spectrum Page:").pack(side=LEFT)
        self.combo_spectrum_page = ttk.Combobox(
            spec_page_frame,
            values=[
                "2 - Warm (Tông ấm/da - KHUYÊN DÙNG)",
                "1 - Rainbow (Cầu vồng)",
                "3 - Gray (Xám)",
                "4 - Hybrid Mode (Auto vuốt trang)",
                "0 - Auto Detect (Tự chọn)"
            ],
            state="readonly",
            width=30
        )
        page_val = config.get("spectrum_page", 2)
        page_map = {2: 0, 1: 1, 3: 2, 4: 3, 0: 4}
        self.combo_spectrum_page.current(page_map.get(page_val, 0))
        self.combo_spectrum_page.pack(side=RIGHT)
        self.combo_spectrum_page.bind("<<ComboboxSelected>>", lambda e: self.on_setting_changed())

        # Number of Painting Colors
        self.var_num_colors = tk.IntVar(value=config.get("num_painting_colors", 8))
        self._create_slider(proc_lf, "Number of Colors (K-Means):", self.var_num_colors, 4, 16)

        # Edge Mode
        mode_frame = ttk.Frame(proc_lf)
        mode_frame.pack(fill=X, pady=2)
        ttk.Label(mode_frame, text="Edge Algorithm:").pack(side=LEFT)
        self.combo_mode = ttk.Combobox(mode_frame, values=["canny", "adaptive", "bilateral"], state="readonly", width=16)
        self.combo_mode.set(config.get("edge_mode", "canny"))
        self.combo_mode.pack(side=RIGHT)
        self.combo_mode.bind("<<ComboboxSelected>>", lambda e: self.on_setting_changed())

        self.var_canny_lower = tk.IntVar(value=config.get("canny_lower", 30))
        self._create_slider(proc_lf, "Edge Sensitivity Low:", self.var_canny_lower, 5, 150)

        self.var_canny_upper = tk.IntVar(value=config.get("canny_upper", 100))
        self._create_slider(proc_lf, "Edge Sensitivity High:", self.var_canny_upper, 20, 220)

        self.var_epsilon = tk.DoubleVar(value=config.get("epsilon", 0.3))
        self._create_slider(proc_lf, "Line Simplification:", self.var_epsilon, 0.0, 3.0, resolution=0.1)

        self.var_min_len = tk.IntVar(value=config.get("min_contour_length", 2))
        self._create_slider(proc_lf, "Min Feature Length:", self.var_min_len, 1, 15)

        self.var_optimize = tk.BooleanVar(value=config.get("optimize_path", True))
        chk_opt = ttk.Checkbutton(proc_lf, text="Optimize Path Order (Greedy TSP)", variable=self.var_optimize, command=self.on_setting_changed, bootstyle="round-toggle")
        chk_opt.pack(anchor=W, pady=(5, 0))

        # 4. Calibration & Execution
        ctrl_lf = ttk.Labelframe(left_frame, text="4. Calibration & Execution", padding=10)
        ctrl_lf.pack(fill=X, pady=(0, 10))

        self.var_fast_mode = tk.BooleanVar(value=config.get("fast_drawing_mode", True))
        chk_fast = ttk.Checkbutton(ctrl_lf, text="Win32 Native Hardware Input (120 FPS)", variable=self.var_fast_mode, command=self.on_setting_changed, bootstyle="success-round-toggle")
        chk_fast.pack(anchor=W, pady=(0, 5))

        btn_grid = ttk.Frame(ctrl_lf)
        btn_grid.pack(fill=X)

        self.btn_calibrate = ttk.Button(btn_grid, text="1. Calibrate Canvas", command=self.start_calibration, bootstyle="primary")
        self.btn_calibrate.pack(side=LEFT, fill=X, expand=True, padx=(0, 2), pady=2)

        self.btn_calib_color = ttk.Button(btn_grid, text="Calibrate Spectrum Bar", command=self.start_color_bar_calibration, bootstyle="secondary")
        self.btn_calib_color.pack(side=RIGHT, fill=X, expand=True, padx=(2, 0), pady=2)

        self.btn_draw = ttk.Button(ctrl_lf, text="2. Start Full Image Reconstruction!", command=self.start_drawing, bootstyle="success")
        self.btn_draw.pack(fill=X, pady=3)

        lbl_hotkeys = ttk.Label(
            ctrl_lf, 
            text=f"Hotkeys: Pause = '{config.get('pause_key','space').upper()}' | Stop = '{config.get('stop_key','q').upper()}'",
            bootstyle="warning"
        )
        lbl_hotkeys.pack(anchor=CENTER, pady=(5, 0))

        # === RIGHT PANEL ===
        prev_lf = ttk.Labelframe(right_frame, text="Live Masterpiece Reconstruction Preview", padding=10)
        prev_lf.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.preview_canvas = tk.Canvas(prev_lf, bg="#1a1a2e", highlightthickness=0)
        self.preview_canvas.pack(fill=BOTH, expand=True)

        self.lbl_stats = ttk.Label(prev_lf, text="Layers: 0 | Strokes: 0", bootstyle="info")
        self.lbl_stats.pack(anchor=W, pady=(5, 0))

        prog_frame = ttk.Frame(right_frame)
        prog_frame.pack(fill=X, pady=(0, 5))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100, bootstyle="success-striped")
        self.progress_bar.pack(fill=X)

        self.lbl_status = ttk.Label(right_frame, text="Status: Ready", relief=SUNKEN, padding=5)
        self.lbl_status.pack(fill=X, pady=(0, 5))

        console_lf = ttk.Labelframe(right_frame, text="Console Feed", padding=5)
        console_lf.pack(fill=BOTH, expand=True)

        self.console_text = ScrolledText(console_lf, height=6, wrap=WORD, bg="#161625", fg="#00ffcc", insertbackground="white")
        self.console_text.pack(fill=BOTH, expand=True)

        redirector = QueueRedirector(console_queue)
        sys.stdout = redirector
        sys.stderr = redirector

        self.root.after(100, self._check_console_queue)

    def _create_slider(self, parent, label_text, var, from_, to, resolution=1):
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=2)

        lbl_title = ttk.Label(frame, text=label_text, width=22, anchor=W)
        lbl_title.pack(side=LEFT)

        val_lbl = ttk.Label(frame, text=f"{var.get():.1f}" if isinstance(var.get(), float) else str(var.get()), width=5, anchor=E)
        val_lbl.pack(side=RIGHT)

        def on_slide(val):
            v = float(val) if isinstance(var.get(), float) else int(float(val))
            var.set(v)
            val_lbl.config(text=f"{v:.1f}" if isinstance(v, float) else str(v))
            self.on_setting_changed()

        scale = ttk.Scale(frame, from_=from_, to=to, value=var.get(), command=on_slide)
        scale.pack(side=RIGHT, fill=X, expand=True, padx=5)

    def apply_full_painting(self):
        self.combo_color_mode.set("full_painting")
        self.var_num_colors.set(8)
        self.on_setting_changed()
        self.update_status("Applied Full Painting Reconstruction mode!")

    def apply_ultra_detail(self):
        self.combo_color_mode.set("monochrome")
        self.var_epsilon.set(0.2)
        self.var_min_len.set(2)
        self.var_canny_lower.set(25)
        self.var_canny_upper.set(80)
        self.on_setting_changed()
        self.update_status("Applied Ultra Detail Sketch preset.")

    def apply_clean_outline(self):
        self.combo_color_mode.set("monochrome")
        self.var_epsilon.set(1.5)
        self.var_min_len.set(7)
        self.var_canny_lower.set(60)
        self.var_canny_upper.set(160)
        self.on_setting_changed()
        self.update_status("Applied Clean Outline preset.")

    def on_setting_changed(self):
        config["color_mode"] = self.combo_color_mode.get()
        # Parse spectrum page from combobox "1 - Rainbow" -> 1
        spec_page_str = self.combo_spectrum_page.get()
        config["spectrum_page"] = int(spec_page_str[0]) if spec_page_str else 2
        config["num_painting_colors"] = int(self.var_num_colors.get())
        config["edge_mode"] = self.combo_mode.get()
        config["canny_lower"] = int(self.var_canny_lower.get())
        config["canny_upper"] = int(self.var_canny_upper.get())
        config["epsilon"] = round(float(self.var_epsilon.get()), 2)
        config["min_contour_length"] = int(self.var_min_len.get())
        config["optimize_path"] = self.var_optimize.get()
        config["fast_drawing_mode"] = self.var_fast_mode.get()
        save_config()

        if self.preview_debounce_timer:
            self.root.after_cancel(self.preview_debounce_timer)
        self.preview_debounce_timer = self.root.after(200, self._update_preview)

    def select_image(self):
        global selected_image_path
        path = filedialog.askopenfilename(
            title="Select Image to Draw",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All Files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(selected_image_path)) if selected_image_path else "."
        )
        if path:
            selected_image_path = path
            config["default_image_path"] = path
            save_config()
            self.lbl_image_name.config(text=os.path.basename(path))
            self._update_preview()

    def _update_preview(self):
        global current_color_groups, current_img_info, current_stats
        if not selected_image_path or not os.path.exists(selected_image_path):
            self.lbl_status.config(text="Status: No image selected.")
            return

        groups, img_info, preview_img, stats = image_processor.generate_sketch_contours(
            selected_image_path,
            mode=config.get("edge_mode", "canny"),
            canny_lower=config.get("canny_lower", 30),
            canny_upper=config.get("canny_upper", 100),
            epsilon=config.get("epsilon", 0.3),
            min_length=config.get("min_contour_length", 2),
            optimize_path=config.get("optimize_path", True),
            color_mode=config.get("color_mode", "full_painting"),
            num_painting_colors=config.get("num_painting_colors", 8)
        )

        if groups is None:
            self.lbl_status.config(text="Status: Image processing failed.")
            return

        current_color_groups = groups
        current_img_info = img_info
        current_stats = stats

        c_w = self.preview_canvas.winfo_width()
        c_h = self.preview_canvas.winfo_height()
        if c_w < 50 or c_h < 50:
            c_w, c_h = 400, 300

        rgb_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        pil_img.thumbnail((c_w, c_h), Image.Resampling.LANCZOS)

        self.preview_image_tk = ImageTk.PhotoImage(pil_img)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(c_w // 2, c_h // 2, image=self.preview_image_tk, anchor=CENTER)

        self.lbl_stats.config(
            text=f"Color Layers: {stats['color_groups_count']} | Total Strokes: {stats['total_contours']}"
        )
        self.lbl_status.config(text=f"Status: Masterpiece preview updated ({stats['color_groups_count']} colors, {stats['total_contours']} strokes).")

    def update_status(self, msg):
        self.root.after(0, lambda: self.lbl_status.config(text=f"Status: {msg}"))

    def start_calibration(self):
        self.lbl_status.config(text="Status: Calibrating canvas area... Check console.")
        self.btn_draw.config(state=DISABLED)
        threading.Thread(target=self._run_calibration, daemon=True).start()

    def _run_calibration(self):
        global canvas_info
        self.root.withdraw()
        time.sleep(0.5)

        print("\n--- CANVAS CALIBRATION ---")
        try:
            print("CLICK top-left corner of drawing canvas area...")
            mouse.wait(mouse.LEFT, target_types=mouse.DOWN)
            x1, y1 = pyautogui.position()
            mouse.wait(mouse.LEFT, target_types=mouse.UP)
            print(f"Top-left set to: ({x1}, {y1})")
            time.sleep(0.5)

            print("CLICK bottom-right corner of drawing canvas area...")
            mouse.wait(mouse.LEFT, target_types=mouse.DOWN)
            x2, y2 = pyautogui.position()
            mouse.wait(mouse.LEFT, target_types=mouse.UP)
            print(f"Bottom-right set to: ({x2}, {y2})")
            time.sleep(0.5)

            w, h = x2 - x1, y2 - y1
            if w <= 0 or h <= 0:
                print("Error: Invalid canvas dimensions!")
                canvas_info = None
                self.update_status("Calibration failed.")
            else:
                center_x = x1 + w / 2.0
                center_y = y1 + h / 2.0
                canvas_info = (x1, y1, w, h, center_x, center_y)
                print(f"Canvas calibrated: {w}x{h} at ({x1},{y1})")
                self.update_status(f"Calibrated canvas ({w}x{h}).")

        except Exception as e:
            print(f"Calibration error: {e}")
            canvas_info = None
            self.update_status(f"Calibration error: {e}")
        finally:
            self.root.deiconify()
            self.btn_draw.config(state=NORMAL)

    def start_color_bar_calibration(self):
        self.lbl_status.config(text="Status: Calibrating Instagram Spectrum Panel... Check console.")
        threading.Thread(target=self._run_color_bar_calibration, daemon=True).start()

    def _run_color_bar_calibration(self):
        global color_bar_info
        self.root.withdraw()
        time.sleep(0.5)

        print("\n--- INSTAGRAM SPECTRUM 5-POINT COMPLETE CALIBRATION (PRESS KEY 'E') ---")
        try:
            def capture_point(prompt_msg):
                print(prompt_msg)
                self.update_status(prompt_msg)
                while keyboard.is_pressed('e'):
                    time.sleep(0.05)
                while not keyboard.is_pressed('e'):
                    time.sleep(0.02)
                cx, cy = pyautogui.position()
                while keyboard.is_pressed('e'):
                    time.sleep(0.05)
                time.sleep(0.3)
                return cx, cy

            print("Hold any swatch on Instagram to open Popover, then capture 5 precise points:\n")

            x1, y1 = capture_point("1. Hover over FAR LEFT EDGE of Popover (Mép trái ngoài cùng) and PRESS KEY 'E'...")
            print(f"   -> Point 1 (Popover Left Edge / x_left): ({x1}, {y1})")

            x2, y2 = capture_point("2. Hover over FAR RIGHT EDGE of Popover (Mép phải ngoài cùng) and PRESS KEY 'E'...")
            print(f"   -> Point 2 (Popover Right Edge / x_right): ({x2}, {y2})")

            x3, y3 = capture_point("3. Hover over TOP EDGE of Popover (Mép trên cùng) and PRESS KEY 'E'...")
            print(f"   -> Point 3 (Popover Top Edge / y_upper): ({x3}, {y3})")

            x4, y4 = capture_point("4. Hover over BOTTOM EDGE of Popover (Mép dưới cùng dải màu) and PRESS KEY 'E'...")
            print(f"   -> Point 4 (Popover Bottom Edge / y_lower): ({x4}, {y4})")

            x5, y5 = capture_point("5. Hover over CENTER of Swatch Circle 1 (Tâm nút tròn #1 bên dưới) and PRESS KEY 'E'...")
            print(f"   -> Point 5 (Swatch Circle Row Center / swatch_y): ({x5}, {y5})")

            # Automatically order X (left < right) and Y (upper < lower)
            x_left = min(x1, x2)
            x_right = max(x1, x2)
            
            # Top of popover is higher up on screen (smaller Y value)
            # Bottom of popover is lower down on screen (larger Y value)
            raw_ys = [y3, y4]
            y_upper = min(raw_ys)
            y_lower = max(raw_ys)
            swatch_y = y5

            spec_w = max(10, abs(x_right - x_left))
            popover_h = max(10, abs(y_lower - y_upper))

            if spec_w <= 10 or popover_h <= 2:
                print("Error: Invalid Spectrum Panel dimensions! Check your calibration points.")
                self.update_status("Spectrum calibration failed - invalid boundaries.")
            else:
                # Store (x_left, y_upper, spec_w, popover_h, y_lower, swatch_y)
                color_bar_info = (x_left, y_upper, spec_w, popover_h, y_lower, swatch_y)
                save_config()
                print(f"\nSpectrum Popover Calibrated 100% 5-Point Perfect:")
                print(f"  X Range (Width): {spec_w}px (from X={x_left} to X={x_right})")
                print(f"  Y Popover Top (y_upper): {y_upper}px (Higher up on monitor)")
                print(f"  Y Popover Bottom (y_lower): {y_lower}px (Popover Height: {popover_h}px)")
                print(f"  Swatch Row Center (swatch_y): {swatch_y}px")
                self.update_status(f"Calibrated 5-Point Spectrum ({spec_w}x{popover_h}px). Press Start!")

        except Exception as e:
            print(f"Spectrum calibration error: {e}")
        finally:
            self.root.deiconify()

    def start_drawing(self):
        if not canvas_info:
            messagebox.showwarning("Warning", "Please calibrate the canvas area first!")
            return

        if not current_color_groups or not current_img_info:
            messagebox.showwarning("Warning", "No valid painting layers to draw!")
            return

        self.btn_draw.config(state=DISABLED)
        self.btn_calibrate.config(state=DISABLED)
        self.progress_var.set(0)
        self.lbl_status.config(text="Status: Preparing full-color reconstruction session...")

        threading.Thread(target=self._run_drawing, daemon=True).start()

    def _run_drawing(self):
        try:
            if not canvas_info or not current_img_info or not current_color_groups:
                self.update_status("Error: Canvas or image data not ready.")
                return

            canvas_x, canvas_y, canvas_w, canvas_h, canvas_cx, canvas_cy = canvas_info

            print("\n--- STARTING FULL IMAGE RECONSTRUCTION PAINTING ---")
            self.update_status("Locating 'plus' icon in Instagram DM...")
            plus_coords = locate_robust(config.get('plus_icons', []))

            if plus_coords is not None:
                pyautogui.click(plus_coords.x, plus_coords.y)
                time.sleep(0.5)
                y_offset = int(config.get('draw_button_y_offset', 75))
                pyautogui.click(plus_coords.x, plus_coords.y - y_offset)
                self.update_status("Drawing interface opened.")
                time.sleep(1)

            self.update_status("Locating thickness slider...")
            thickness_coords = locate_robust(config.get('slider_handles', []))
            if thickness_coords is not None:
                th_offset = int(config.get('thickness_adjust_y_offset', 20))
                pyautogui.click(thickness_coords.x, thickness_coords.y + th_offset)
                self.update_status("Brush thickness set.")
                time.sleep(0.5)

            color_mode = config.get("color_mode", "full_painting")

            if color_mode == "monochrome":
                self.update_status("Select your brush color in Instagram DM, then CLICK mouse to start!")
                print(">>> WAITING FOR USER COLOR SELECTION <<<")
                print("Select your color in Instagram, then CLICK LEFT MOUSE BUTTON anywhere to start...")
                mouse.wait(mouse.LEFT, target_types=mouse.DOWN)
                mouse.wait(mouse.LEFT, target_types=mouse.UP)

            img_w, img_h = current_img_info["width"], current_img_info["height"]
            img_cx, img_cy = current_img_info["center_x"], current_img_info["center_y"]

            scale_x = canvas_w / img_w
            scale_y = canvas_h / img_h
            scale_factor = min(scale_x, scale_y) * config.get('scale_margin', 0.9)

            fast_mode = config.get("fast_drawing_mode", True)

            drawer = FastDrawer(
                pause_key=config.get("pause_key", "space"),
                stop_key=config.get("stop_key", "q"),
                fast_mode=fast_mode,
                step_size=config.get("step_size", 2.0),
                spectrum_page=config.get("spectrum_page", 4)
            )

            def on_progress(cur, total, pct):
                self.root.after(0, lambda: self.progress_var.set(pct))

            drawer.draw_color_groups(
                color_groups=current_color_groups,
                scale_factor=scale_factor,
                canvas_center_x=canvas_cx,
                canvas_center_y=canvas_cy,
                img_center_x=img_cx,
                img_center_y=img_cy,
                color_bar_info=color_bar_info,
                color_mode="spectrum" if color_mode == "full_painting" else color_mode,
                point_delay=config.get("point_delay", 0.002),
                stroke_delay=config.get("stroke_delay", 0.01),
                progress_callback=on_progress,
                status_callback=self.update_status
            )

        except Exception as e:
            print(f"Error during drawing logic: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.root.after(0, lambda: self.btn_draw.config(state=NORMAL))
            self.root.after(0, lambda: self.btn_calibrate.config(state=NORMAL))

    def _check_console_queue(self):
        while not console_queue.empty():
            try:
                text = console_queue.get_nowait()
                self.console_text.insert(END, text)
                self.console_text.see(END)
            except queue.Empty:
                pass
        self.root.after(100, self._check_console_queue)


if __name__ == "__main__":
    load_config()
    root = ttk.Window(themename="vapor")
    app = AutoDoodleApp(root)
    root.mainloop()