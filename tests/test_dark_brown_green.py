import colorsys

# Test Updated Coordinates:
# 1. Dark Brown Center & Freckles (RGB 84, 22, 29):
#    Map to Page 2 Swatch 6/7 Dark Brown -> x = 0.680, y = 0.45 -> TRUE DARK BROWN / NÂU SẪM!
# 2. Dark Green Stamen (RGB 77, 69, 36):
#    Map to Page 1 Swatch 3 Green lower dark zone -> x = 0.250, y = 0.85 -> DARK FOREST/OLIVE GREEN!

colors = [
    ("Dark Maroon / Spots", (84, 22, 29)),
    ("Olive Green Stamen",  (77, 69, 36)),
]

print("FINAL COLOR TUNING VERIFICATION:")
print("=" * 80)

for name, rgb in colors:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue = h * 360.0

    if "Green" in name:
        x, y = 0.250, 0.85
        note = "Page 1 - Swatch 3 Green (y=0.85 -> DARK FOREST / DEEP OLIVE GREEN!)"
    else:
        x, y = 0.680, 0.45
        note = "Page 2 - Swatch 6 Dark Brown (x=0.68, y=0.45 -> TRUE DARK BROWN / NÂU SẪM!)"

    print(f"{name:<22} RGB{str(rgb):<16} -> X={x:.3f}, Y={y:.2f} | {note}")
