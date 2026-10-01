import os
import sys
import colorsys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import drawer

# Modify rainbow_spectrum_pct to fix Olive Green -> Swatch 3 Green and Dark Maroon -> Swatch 1 Black
colors = [
    ("Olive Green (Nhụy)",  (77, 69, 36)),
    ("Dark Maroon (Đầu)",   (84, 22, 29)),
    ("Crimson (Đốm thẫm)", (146, 37, 66)),
]

print("TEST STAMEN & TIPS FIX:")
print("=" * 70)

for name, rgb in colors:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue = h * 360.0

    # Rule fix:
    # 1. Olive Green (25° <= hue <= 80°, r < 130, g > b): map to Swatch 3 Green (x = 0.250)
    # 2. Dark Maroon / Brown tips (v < 0.40 and s > 0.40): map to Swatch 1 Black/Dark Brown (x = 0.02)
    if 25 <= hue <= 80 and r < 130 and g > b:
        x_fix = 0.250  # Swatch 3 Green!
        label = "GREEN (#3) -> Nhụy Xanh Lá!"
    elif v < 0.40:
        x_fix = 0.02   # Swatch 1 Black/Dark Brown!
        label = "BLACK (#1) -> Đầu nhụy Màu Nâu/Đen!"
    else:
        x_fix = 0.750
        label = "DEEP RED/MAGENTA"

    print(f"{name:<20} RGB{str(rgb):<16} Hue={hue:<5.0f} V={v:<4.2f} -> X={x_fix:.3f} ({label})")
