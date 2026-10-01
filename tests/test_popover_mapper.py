import colorsys

# Test the new Spectrum Drag Coordinate Logic
# Goal for Petals (Dusty Pink / Mauve):
# - On Page 2 (Warm): Drag HIGH UP (y_pct = 0.70 to 0.90) and LEFT (x_pct = 0.02 to 0.12) -> Soft Dusty Pink!
# - For Olive Green Stamen: On Page 1 (Rainbow), Swatch 3 Green (x_pct = 0.250), drag to LOWER-MID (y_pct = 0.40) -> Olive Green!
# - For Dark Maroon Tips: On Page 1 or 2, Black/Maroon area (x_pct = 0.02), drag NEAR BOTTOM (y_pct = 0.15) -> Dark Maroon!

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

def map_spectrum_color(rgb, page=2):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue = h * 360.0
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # 1. Olive Green Stamen
    if 25 <= hue <= 85 and r < 130 and g > b:
        return (0.250, 0.35, "Page 1 - Swatch 3 Green (Drag mid -> Olive Green)")

    # 2. Dark Maroon Tips & Spots
    if v < 0.40 and s > 0.30:
        return (0.020, 0.15, "Page 1/2 - Swatch 1 Black (Drag bottom -> Dark Maroon/Plum)")

    # 3. Petals on Page 2 (Warm)
    # X-axis: Map to far left Swatch 1/2 (x = 0.02 to 0.12)
    if hue >= 300 or hue <= 35:
        if hue >= 300:
            x_pct = 0.02 + (hue - 300) / 60.0 * 0.08
        else:
            x_pct = 0.08 + hue / 35.0 * 0.06
    else:
        x_pct = 0.15

    # Y-axis (Popover Height):
    # Luma 0.80 (very light) -> y_pct = 0.85 (High up in popover -> Light Pastel Pink!)
    # Luma 0.60 (dusty rose) -> y_pct = 0.65 (Upper-mid in popover -> Dusty Rose!)
    y_pct = 0.30 + luma * 0.55

    return (x_pct, y_pct, "Page 2 - Swatch 1/2 (Drag HIGH UP -> Soft Dusty Pink!)")

print("NEW SPECTRUM POPOVER MAPPER TEST:")
print("=" * 85)
print(f"{'Color':<15} {'RGB':<17} {'X% (Left)':<12} {'Y% (Upward)':<14} {'Target Instagram Popover Zone'}")
print("-" * 85)

for name, rgb in colors:
    x, y, note = map_spectrum_color(rgb)
    print(f"{name:<15} {str(rgb):<17} {x:<12.3f} {y:<14.2f} {note}")
