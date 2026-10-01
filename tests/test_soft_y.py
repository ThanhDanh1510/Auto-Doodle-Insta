import os
import sys
import colorsys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import drawer

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

print("CURRENT vs PROPOSED Y-SHIFT FOR MUTED SOFT LOOK:")
print("=" * 80)
print(f"{'Color':<14} {'RGB':<17} {'S':<5} {'V':<5} {'Current Y':<10} {'New Soft Y':<10} {'Target Look'}")
print("-" * 80)

for name, rgb in colors:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    curr_y = 0.05 + (1.0 - luma) * 0.90

    # Soft/Muted Y-shift: shift Y downward (+0.22) into muted/matte zone if S < 0.65
    if s < 0.65:
        new_y = min(0.85, curr_y + 0.22)
    else:
        new_y = curr_y

    look = "Soft Dusty Matte Pink (Dịu chuẩn gốc)" if s < 0.65 else "Deep Rich Accent"
    print(f"{name:<14} {str(rgb):<17} {s:<5.2f} {v:<5.2f} {curr_y:<10.2f} {new_y:<10.2f} {look}")
