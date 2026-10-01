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
]

print("PAGE 2 (WARM) - PASTEL LIGHT SHIFT TEST:")
print("=" * 75)
print(f"{'Color':<14} {'RGB':<17} {'S':<5} {'V':<5} {'X% (Left)':<12} {'Y% (Top=Light)':<15}")
print("-" * 75)

for name, rgb in colors:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue = h * 360.0

    # Force X to left pastel zone (Swatch 1 & 2: x = 0.02 to 0.12)
    if hue >= 300 or hue <= 35:
        # Scale hue between 300->360 to x = 0.01 -> 0.10
        if hue >= 300:
            x_pct = 0.01 + (hue - 300) / 60.0 * 0.09
        else:
            x_pct = 0.10 + hue / 35.0 * 0.08
    else:
        x_pct = 0.20

    # Force Y to TOP/UPPER region (y = 0.12 to 0.35) for LIGHT PASTEL PINK!
    # Luma 0.80 -> y = 0.12 (very light pink/white)
    # Luma 0.55 -> y = 0.35 (soft light pink)
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    y_pct = 0.10 + (1.0 - luma) * 0.50

    print(f"{name:<14} {str(rgb):<17} {s:<5.2f} {v:<5.2f} {x_pct:<12.3f} {y_pct:<15.2f}")
