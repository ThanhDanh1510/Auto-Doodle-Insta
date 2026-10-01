import colorsys
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vision import generate_full_painting_layers

sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'samples', 'Lily.png'))
layers, info, preview = generate_full_painting_layers(sample_path, num_colors=12, fill_step=2)
assert layers is not None

palette_rgb = [l["rgb"] for l in layers]

print("Color Analysis for Lily.png:")
print("=" * 60)

cool_count = 0
warm_count = 0
gray_count = 0

for rgb in palette_rgb:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    hue_deg = h * 360.0

    if s < 0.10:
        c_type = "Gray/Neutral"
        gray_count += 1
    elif 70 <= hue_deg <= 280:
        c_type = "Cool (Blue/Green/Cyan)"
        cool_count += 1
    else:
        c_type = "Warm (Pink/Red/Orange/Peach)"
        warm_count += 1

    print(f"RGB{str(rgb):<16} Hue={hue_deg:<5.0f} S={s:<4.2f} V={v:<4.2f} -> {c_type}")

print("=" * 60)
print(f"Summary: Warm={warm_count}, Cool={cool_count}, Gray={gray_count}")

if cool_count > 0:
    recommended = "Page 1 - Rainbow (Có màu Xanh lá/Xanh dương/Tím lạnh)"
elif warm_count > 0:
    recommended = "Page 2 - Warm (Toàn bộ là tông Ấm: Hồng/Đỏ/Cam/Da)"
else:
    recommended = "Page 3 - Gray (Toàn bộ là màu Xám/Trắng/Đen)"

print(f"Recommended Instagram Spectrum Page: {recommended}")
