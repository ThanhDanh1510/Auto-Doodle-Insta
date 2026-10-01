import colorsys
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vision import generate_full_painting_layers

sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'samples', 'Lily.png'))
layers, info, preview = generate_full_painting_layers(sample_path, num_colors=12, fill_step=2)
assert layers is not None

def rgb_to_hex(rgb):
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

print("DANH SÁCH MÃ MÀU DÙNG CHO HÌNH PREVIEW LILY.PNG:")
print("=" * 80)
print(f"{'STT':<4} {'Mã HEX':<10} {'Mã RGB':<18} {'HSV (H°, S%, V%)':<22} {'Diện tích (px)':<15} {'Mô tả màu'}")
print("-" * 80)

total_area = sum(l["area"] for l in layers)

for i, l in enumerate(layers):
    rgb = l["rgb"]
    hex_code = rgb_to_hex(rgb)
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    h_deg = int(h * 360)
    s_pct = int(s * 100)
    v_pct = int(v * 100)
    area = l["area"]
    pct = (area / total_area) * 100

    # Human-readable color naming
    if s < 0.10:
        desc = "Trắng xám / Trung tính"
    elif 25 <= h_deg <= 85 and rgb[0] < 130 and rgb[1] > rgb[2]:
        desc = "🌿 Nhụy Xanh Lá (Stamen Green)"
    elif v_pct < 40:
        desc = "🟤 Đầu nhụy / Đốm hạt Nâu Đen"
    elif s_pct <= 30:
        desc = "🌸 Hồng nhạt pastel / Phấn (Pale Pink)"
    elif s_pct <= 45:
        desc = "🌸 Hồng Mauve dịu (Light Mauve)"
    elif s_pct <= 60:
        desc = "🌸 Hồng Rose mờ (Muted Rose)"
    else:
        desc = "🌺 Hồng Đậm / Đỏ thẫm (Deep Crimson)"

    print(f"Lớp {i+1:<2} {hex_code:<10} RGB{str(rgb):<15} {h_deg}° {s_pct}% {v_pct}% ({pct:4.1f}%)    {area:<15} {desc}")
