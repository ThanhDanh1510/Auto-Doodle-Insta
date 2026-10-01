import colorsys

# Target: Dark Deep Crimson Red (Đỏ sẫm thẫm) for flower center & spots (RGB 84, 22, 29)
# Swatch 9 Red (x = 0.960) bottom dark region (y_pct = 0.20) -> DEEP BLOOD RED / DARK CRIMSON (Đỏ sẫm thẫm)!

colors = [
    ("Dark Crimson Center & Spots", (84, 22, 29)),
    ("Olive Green Stamen", (77, 69, 36)),
]

print("DEEP CRIMSON RED TARGET TEST:")
print("=" * 80)

for name, rgb in colors:
    if "Crimson" in name:
        x, y = 0.960, 0.20  # Swatch 9 Red lower dark region
        note = "Swatch 9 Red lower dark zone (y=0.20 -> DEEP BLOOD RED / ĐỎ SẪM THẪM!)"
    else:
        x, y = 0.250, 0.15  # Swatch 3 Green lower dark zone
        note = "Swatch 3 Green lower dark zone (y=0.15 -> DARK FOREST / DEEP OLIVE GREEN!)"

    print(f"{name:<30} RGB{str(rgb):<16} -> X={x:.3f}, Y={y:.2f} | {note}")
