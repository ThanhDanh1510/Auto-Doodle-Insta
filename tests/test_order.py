import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vision import generate_full_painting_layers

sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'samples', 'Lily.png'))
layers, info, preview = generate_full_painting_layers(sample_path, num_colors=12, fill_step=2)
assert layers is not None

print("Thu tu ve (dien tich lon nhat truoc):")
print("=" * 70)
for i, l in enumerate(layers):
    name = l["name"]
    area = l["area"]
    strokes = len(l["contours"])
    rgb = l["rgb"]
    print(f"  Layer {i+1}: RGB{rgb} - area={area}px - {strokes} strokes")
