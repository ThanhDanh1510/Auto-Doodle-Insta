import colorsys
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.automation import warm_spectrum_pct

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

print("PAGE 2 (WARM SPECTRUM) COMPLETE ALL-LAYER MAPPING:")
print("=" * 80)
print(f"{'Layer Color':<15} {'RGB':<18} {'X%':<8} {'Y%':<8} {'Page 2 Swatch Target'}")
print("-" * 80)

for name, rgb in colors:
    x, y = warm_spectrum_pct(rgb)
    
    if rgb == (84, 22, 29):
        desc = "Swatch 7/8 Dark Maroon (Đầu nhụy & đốm thẫm)"
    elif rgb == (77, 69, 36):
        desc = "Swatch 5 Warm Olive (Thân nhụy)"
    elif rgb in [(146, 37, 66), (158, 63, 91)]:
        desc = "Swatch 6/7 Deep Rose/Crimson (Nét gân đậm)"
    else:
        desc = "Swatch 1/2 Soft Pastel Pink/Mauve (Cánh hoa mờ dịu)"

    print(f"{name:<15} {str(rgb):<18} {x:<8.3f} {y:<8.2f} {desc}")
