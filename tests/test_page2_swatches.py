import colorsys

# Corrected 9 Swatches of Page 2 (Warm)
# x = 0.000: Swatch 1 - Dusty Rose (Hồng đất)
# x = 0.125: Swatch 2 - Pale Pink (Hồng phấn nhạt)
# x = 0.250: Swatch 3 - Cream Beige (Beige nhạt)
# x = 0.375: Swatch 4 - Peach (Cam đào)
# x = 0.500: Swatch 5 - Ochre (Nâu sáng)
# x = 0.625: Swatch 6 - Dark Brown (Nâu đất)
# x = 0.750: Swatch 7 - Off-black (Đen xám)
# x = 0.875: Swatch 8 - Dark Gray (Xám thẫm)
# x = 1.000: Swatch 9 - Medium Gray (Xám vừa)

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

def warm_spectrum_pct_v3(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # 1. Olive Green Stamen -> Swatch 5 Ochre/Nâu sáng (x = 0.500)
    if 25 <= hue <= 85 and r < 130 and g > b:
        return (0.500, 0.40, "Swatch 5 Ochre/Nâu sáng (Stamen)")

    # 2. Dark Maroon / Brown tips & spots -> Swatch 7 Off-black (x = 0.750) or Swatch 6 (x = 0.625)
    if v < 0.40 and s > 0.30:
        return (0.750, 0.20, "Swatch 7 Off-black/Đen xám (Tips)")

    # Grayscale
    if s < 0.08:
        return (0.875 if v < 0.40 else 1.000, 0.50, "Achromatic Gray")

    # 3. Petals (Pink/Red/Peach) -> Map to Swatch 1, 2, 3 (x = 0.0 to 0.25)
    if hue >= 300 or hue <= 15:
        # Dusty Rose / Pale Pink / Beige
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

    # Y-axis: Drag high up for pastel lightness
    y_pct = 0.30 + luma * 0.55

    return (x_pct, y_pct, f"Swatch at x={x_pct:.3f}")

print("CORRECTED 9-SWATCH PAGE 2 MAPPING ANALYSIS:")
print("=" * 90)
for name, rgb in colors:
    x, y, desc = warm_spectrum_pct_v3(rgb)
    print(f"{name:<15} RGB{str(rgb):<18} X={x:<8.3f} Y={y:<8.2f} {desc}")
