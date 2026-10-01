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

def choose_best_page_for_color_v2(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue_deg = h * 360.0

    if s < 0.08:
        return 3  # Gray page

    # Increase S threshold to 0.62 so soft/dusted pink petals stay on Page 2 (Warm)
    # to avoid Instagram's harsh hot magenta on Page 1!
    if s <= 0.62 and v >= 0.40 and (hue_deg >= 300 or hue_deg <= 35):
        return 2  # Warm page (Soft Muted Pink/Mauve/Peach)
    else:
        return 1  # Rainbow page (Ultra-deep Crimson, Dark Maroon, Cool colors)

print("UPDATED HYBRID PAGE SELECTION (S <= 0.62 -> Page 2 Warm):")
print("=" * 80)
print(f"{'Layer Color':<15} {'RGB':<18} {'H°':<5} {'S':<5} {'V':<5} {'Target Page':<15} {'Effect'}")
print("-" * 80)

for name, rgb in colors:
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    page = choose_best_page_for_color_v2(rgb)
    p_name = "Page 2 (Warm)" if page == 2 else ("Page 1 (Rainbow)" if page == 1 else "Page 3 (Gray)")
    effect = "Trầm dịu chuẩn ảnh gốc (Soft Muted)" if page == 2 else "Gân nhụy & nét tối đậm (Dark Outlines)"
    print(f"{name:<15} {str(rgb):<18} {h*360:<5.0f} {s:<5.2f} {v:<5.2f} {p_name:<15} {effect}")
