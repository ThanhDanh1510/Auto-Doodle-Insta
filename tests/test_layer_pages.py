import colorsys
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.automation import choose_best_page_for_color
from src.vision import generate_full_painting_layers

sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'samples', 'Lily.png'))
layers, info, preview = generate_full_painting_layers(sample_path, num_colors=12, fill_step=2)
assert layers is not None

print("DETAILED LAYER PAGE ANALYSIS FOR LILY.PNG:")
print("=" * 80)
for i, l in enumerate(layers):
    rgb = l["rgb"]
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    h_deg = int(h * 360)
    s_pct = int(s * 100)
    v_pct = int(v * 100)
    page = choose_best_page_for_color(rgb)
    p_name = "PAGE 2 (WARM)" if page == 2 else ("PAGE 1 (RAINBOW)" if page == 1 else "PAGE 3 (GRAY)")
    print(f"Layer {i+1:<2} RGB{str(rgb):<16} H={h_deg:<3}° S={s_pct:<2}% V={v_pct:<2}% -> {p_name}")
