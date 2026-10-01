import colorsys

# Test new target coordinates:
# 1. Olive Green Stamen: (0.250, 0.68) -> Deep rich moss/olive green!
# 2. Dark Maroon / Brown center outlines & spots: (0.960, 0.68) on Swatch 9 Red popover -> Dark Blood Red / Maroon / Plum Brown!

colors = [
    ("Dark Maroon (Tâm)", (84, 22, 29)),
    ("Olive Green (Nhụy)",  (77, 69, 36)),
]

print("PROPOSED SPECTRUM TUNING:")
print("=" * 80)
for name, rgb in colors:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue = h * 360.0

    if name.startswith("Olive"):
        x, y = 0.250, 0.68
        desc = "Swatch 3 (Green) popover lower area -> Deep Moss/Olive Green (Đẫm hơn!)"
    else:
        x, y = 0.960, 0.68
        desc = "Swatch 9 (Red) popover lower-mid area -> Dark Blood Red/Maroon/Plum Brown (Không bị đen xì!)"

    print(f"{name:<20} RGB{str(rgb):<16} -> X={x:.3f}, Y={y:.2f} | {desc}")
