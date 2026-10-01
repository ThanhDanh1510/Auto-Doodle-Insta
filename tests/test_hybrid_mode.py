import colorsys

colors = [
    ("Dark Rose",    (171, 77, 116)),
    ("Muted Pink",   (168, 106, 125)),
    ("Light Mauve",  (195, 117, 147)),
    ("Pale Pink",    (197, 148, 158)),
    ("Medium Pink",  (188, 93, 133)),
    ("Beige",        (204, 176, 171)),
    ("Gray-Pink",    (171, 137, 136)),
    ("Deep Rose",    (158, 63, 91)),
    ("Crimson",      (146, 37, 66)),
    ("Dark Maroon",  (84, 22, 29)),
    ("Olive Green",  (77, 69, 36)),
]

def choose_best_page_for_color(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue_deg = h * 360.0

    if s < 0.08:
        return 3  # Gray page for pure monochrome

    # Key distinction:
    # Page 2 (Warm): Low-to-medium saturation (muted pastel pinks, pale mauve, beige, skin)
    # Page 1 (Rainbow): High saturation vivid pinks, deep crimson, dark maroon, cool colors

    if s <= 0.42 and v >= 0.50 and (hue_deg >= 310 or hue_deg <= 30):
        # Muted pastel tones -> Page 2 (Warm)
        return 2
    else:
        # Vivid, saturated, or dark deep tones -> Page 1 (Rainbow)
        return 1

print("HYBRID MODE - PAGE SELECTION PER LILY LAYER:")
print("=" * 80)
print(f"{'Layer Color':<15} {'RGB':<18} {'H°':<5} {'S':<5} {'V':<5} {'Selected Page':<15} {'Reason'}")
print("-" * 80)

for name, rgb in colors:
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    page = choose_best_page_for_color(rgb)
    p_name = "Page 2 (Warm)" if page == 2 else ("Page 1 (Rainbow)" if page == 1 else "Page 3 (Gray)")
    reason = "Muted/Pastel Pink (Tránh bị quá rực)" if page == 2 else "Vivid/Dark Deep Tone (Lấy hồng đậm/đỏ thẫm)"
    print(f"{name:<15} {str(rgb):<18} {h*360:<5.0f} {s:<5.2f} {v:<5.2f} {p_name:<15} {reason}")
