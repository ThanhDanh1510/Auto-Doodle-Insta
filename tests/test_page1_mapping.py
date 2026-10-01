import colorsys
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.automation import rainbow_spectrum_pct

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

print("PAGE 1 (RAINBOW) SPECTRUM MAPPING FOR LILY COLORS:")
print("=" * 75)
print(f"{'Color':<15} {'RGB':<18} {'H':<5} {'S':<5} {'V':<5} {'X%':<6} {'Y%':<6} {'Page 1 Position'}")
print("-" * 75)

for name, rgb in colors:
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    x, y = rainbow_spectrum_pct(rgb)
    print(f"{name:<15} {str(rgb):<18} {h*360:<5.0f} {s:<5.2f} {v:<5.2f} {x:<6.2f} {y:<6.2f} Right-side Vivid Pink Zone")
