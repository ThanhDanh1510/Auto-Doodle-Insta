import os
import sys
import colorsys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import drawer
import painter_engine

colors = [
    ("Dark Rose",    (171,77,116)),
    ("Muted Pink",   (168,106,125)),
    ("Light Mauve",  (195,117,147)),
    ("Pale Pink",    (197,148,158)),
    ("Medium Pink",  (188,93,133)),
    ("Beige",        (204,176,171)),
    ("Gray-Pink",    (171,137,136)),
    ("Deep Rose",    (158,63,91)),
    ("Crimson",      (146,37,66)),
    ("Dark Maroon",  (84,22,29)),
    ("Olive Green",  (77,69,36)),
]

def get_zone(x):
    swatches = [
        (0.000, "DEN (#1)"),
        (0.125, "XANH DUONG (#2)"),
        (0.250, "XANH LA (#3)"),
        (0.375, "VANG (#4)"),
        (0.500, "CAM (#5)"),
        (0.625, "DO SAN HO (#6)"),
        (0.750, "HONG DAM (#7)"),
        (0.875, "TIM (#8)"),
        (1.000, "DO (#9)"),
    ]
    closest = min(swatches, key=lambda s: abs(s[0] - x))
    return closest[1]

print("PAGE 1 (Rainbow) - 9 Swatches - Mapping cho hoa Lily")
print("=" * 90)
print(f"{'Color':<14} {'RGB':<17} {'H':<5} {'S':<5} {'V':<5} {'X%':<6} {'Y%':<6} {'Nearest Swatch'}")
print("-" * 90)
for name, rgb in colors:
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    x, y = drawer.rainbow_spectrum_pct(rgb)
    zone = get_zone(x)
    print(f"{name:<14} {str(rgb):<17} {h*360:<5.0f} {s:<5.2f} {v:<5.2f} {x:<6.3f} {y:<6.2f} {zone}")

print()
sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'samples', 'Lily.png'))
layers, info, preview = painter_engine.generate_full_painting_layers(sample_path, num_colors=12, fill_step=2)
page = drawer.auto_detect_spectrum_page(layers)
print(f"Auto-detect: Lily.png -> Page {page} ({'Rainbow' if page==1 else 'Warm' if page==2 else 'Gray'})")
