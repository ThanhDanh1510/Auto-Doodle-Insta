import cv2
import numpy as np
import os
import math
import colorama
from colorama import Fore, Style
try:
    import painter_engine
except ImportError:
    from . import painter_engine

colorama.init(autoreset=True)

INSTAGRAM_DEFAULT_PALETTE = [
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


def rgb_to_lab(rgb_color):
    bgr_pixel = np.uint8([[[rgb_color[2], rgb_color[1], rgb_color[0]]]])
    lab_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2LAB)
    return lab_pixel[0][0].astype(np.float32)


def color_distance_lab(rgb1, rgb2):
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    return np.linalg.norm(lab1 - lab2)


def sample_contour_color(image_bgr, contour):
    h, w, _ = image_bgr.shape
    sampled_colors = []
    step = max(1, len(contour) // 20)
    for i in range(0, len(contour), step):
        pt = contour[i]
        px, py = int(pt[0]), int(pt[1])
        if 0 <= px < w and 0 <= py < h:
            bgr = image_bgr[py, px]
            sampled_colors.append((int(bgr[2]), int(bgr[1]), int(bgr[0])))

    if not sampled_colors:
        return (0, 0, 0)

    avg_r = int(np.mean([c[0] for c in sampled_colors]))
    avg_g = int(np.mean([c[1] for c in sampled_colors]))
    avg_b = int(np.mean([c[2] for c in sampled_colors]))
    return (avg_r, avg_g, avg_b)


def sort_contours_greedy(contours):
    if not contours:
        return []

    unvisited = contours.copy()
    sorted_contours = []
    current = unvisited.pop(0)
    sorted_contours.append(current)

    while unvisited:
        last_point = current[-1]
        best_idx = 0
        best_dist = float('inf')
        should_reverse = False

        for idx, cnt in enumerate(unvisited):
            start_pt = cnt[0]
            end_pt = cnt[-1]
            d_start = math.hypot(last_point[0] - start_pt[0], last_point[1] - start_pt[1])
            d_end = math.hypot(last_point[0] - end_pt[0], last_point[1] - end_pt[1])

            if d_start < best_dist:
                best_dist = d_start
                best_idx = idx
                should_reverse = False

            if d_end < best_dist:
                best_dist = d_end
                best_idx = idx
                should_reverse = True

        next_cnt = unvisited.pop(best_idx)
        if should_reverse:
            next_cnt = next_cnt[::-1]

        sorted_contours.append(next_cnt)
        current = next_cnt

    return sorted_contours


def simplify_contour(cnt, epsilon_val):
    if epsilon_val <= 0:
        return [(int(p[0][0]), int(p[0][1])) for p in cnt]
    approx = cv2.approxPolyDP(cnt, epsilon_val, False)
    return [(int(p[0][0]), int(p[0][1])) for p in approx]


def generate_sketch_contours(
    image_path,
    mode="canny",
    canny_lower=50,
    canny_upper=150,
    blur_kernel=5,
    epsilon=1.0,
    min_length=4,
    optimize_path=True,
    color_mode="monochrome",  # "monochrome", "palette", "spectrum", "full_painting"
    num_painting_colors=8,
    status_callback=None
):
    """
    Processes an input image and extracts sketch contours or full-color reconstruction layers.
    :return: (color_groups, img_info, preview_canvas, stats)
    """
    def log_status(msg):
        print(msg)
        if status_callback:
            status_callback(msg)

    if not os.path.exists(image_path):
        log_status(f"{Fore.RED}Error: Image file '{image_path}' not found.")
        return None, None, None, None

    # Full Painting Reconstruction Engine Mode
    if color_mode == "full_painting":
        log_status(f"{Fore.CYAN}Generating Full-Color Painting ({num_painting_colors} colors)...")
        layers, img_info, preview_canvas = painter_engine.generate_full_painting_layers(
            image_path, num_colors=num_painting_colors, fill_step=2
        )
        if layers is None:
            log_status(f"{Fore.RED}Error: Full painting generation failed.")
            return None, None, None, None

        total_contours = sum(len(g["contours"]) for g in layers)
        total_points = sum(sum(len(c) for c in g["contours"]) for g in layers)

        stats = {
            "total_contours": total_contours,
            "color_groups_count": len(layers),
            "original_points": total_points,
            "simplified_points": total_points,
            "reduction_percent": 0.0,
        }
        log_status(f"{Fore.GREEN}Full painting ready: {len(layers)} color layers, {total_contours} strokes.")
        return layers, img_info, preview_canvas, stats

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        log_status(f"{Fore.RED}Error: Could not read image '{image_path}'.")
        return None, None, None, None

    img_height, img_width, _ = image_bgr.shape
    img_info = {
        "height": img_height,
        "width": img_width,
        "center_x": img_width / 2.0,
        "center_y": img_height / 2.0,
    }

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_k = max(1, int(blur_kernel))
    if blur_k % 2 == 0:
        blur_k += 1

    if mode == "bilateral":
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.Canny(filtered, canny_lower, canny_upper)
    elif mode == "adaptive":
        blurred = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        edges = cv2.Canny(binary, canny_lower, canny_upper)
    else:  # Standard Canny
        blurred = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
        edges = cv2.Canny(blurred, canny_lower, canny_upper)

    raw_contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    original_point_count = sum(len(c) for c in raw_contours)

    preview_canvas = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255
    color_groups = []

    if color_mode == "monochrome":
        mono_contours = []
        for cnt in raw_contours:
            simplified = simplify_contour(cnt, epsilon)
            if len(simplified) >= min_length:
                mono_contours.append(simplified)
        if optimize_path and mono_contours:
            mono_contours = sort_contours_greedy(mono_contours)

        for cnt in mono_contours:
            if len(cnt) > 1:
                pts = np.array(cnt, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(preview_canvas, [pts], isClosed=False, color=(0, 0, 0), thickness=1)

        color_groups.append({
            "name": "Black",
            "rgb": (0, 0, 0),
            "pct": 0.15,
            "contours": mono_contours
        })
    else:
        swatch_groups = {i: [] for i in range(len(INSTAGRAM_DEFAULT_PALETTE))}

        for cnt in raw_contours:
            simplified = simplify_contour(cnt, epsilon)
            if len(simplified) < min_length:
                continue

            sampled_rgb = sample_contour_color(image_bgr, simplified)
            best_idx = min(
                range(len(INSTAGRAM_DEFAULT_PALETTE)),
                key=lambda idx: color_distance_lab(sampled_rgb, INSTAGRAM_DEFAULT_PALETTE[idx]["rgb"])
            )
            swatch_groups[best_idx].append((simplified, sampled_rgb if color_mode == "spectrum" else INSTAGRAM_DEFAULT_PALETTE[best_idx]["rgb"]))

        for idx, items in swatch_groups.items():
            if not items:
                continue
            swatch_info = INSTAGRAM_DEFAULT_PALETTE[idx]
            group_contours = [item[0] for item in items]
            if optimize_path:
                group_contours = sort_contours_greedy(group_contours)

            bgr_color = (swatch_info["rgb"][2], swatch_info["rgb"][1], swatch_info["rgb"][0])
            for cnt in group_contours:
                if len(cnt) > 1:
                    pts = np.array(cnt, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(preview_canvas, [pts], isClosed=False, color=bgr_color, thickness=1)

            color_groups.append({
                "name": swatch_info["name"],
                "rgb": swatch_info["rgb"],
                "pct": swatch_info["pct"],
                "contours": group_contours
            })

    total_contours = sum(len(g["contours"]) for g in color_groups)
    simplified_point_count = sum(sum(len(c) for c in g["contours"]) for g in color_groups)
    reduction = 0.0
    if original_point_count > 0:
        reduction = (1.0 - (simplified_point_count / original_point_count)) * 100.0

    stats = {
        "total_contours": total_contours,
        "color_groups_count": len(color_groups),
        "original_points": original_point_count,
        "simplified_points": simplified_point_count,
        "reduction_percent": round(reduction, 1),
    }

    log_status(
        f"{Fore.GREEN}Processed image: {total_contours} contours in {len(color_groups)} colors, "
        f"{simplified_point_count} points."
    )

    return color_groups, img_info, preview_canvas, stats