import colorsys

# Correct Y-axis Popover Mechanics:
# - Top of Popover (y_pct = 0.70 to 0.85) -> Light Pastel Colors (Mint Green, Soft Pink, Cream)
# - Bottom of Popover (y_pct = 0.10 to 0.25) -> Dark Shaded Colors (Dark Forest Green, Dark Brown, Charcoal)

colors = [
    ("Dark Brown Center & Spots", (84, 22, 29)),
    ("Dark Olive/Forest Green Stamen", (77, 69, 36)),
    ("Soft Dusty Pink Petals", (171, 77, 116)),
]

print("CORRECT POPOVER Y-MECHANICS TEST:")
print("=" * 85)

for name, rgb in colors:
    if "Brown" in name:
        x, y = 0.020, 0.15  # Swatch 1 Black/Dark Brown bottom dark zone
        note = "Swatch 1 bottom dark zone (y=0.15 -> DEEP DARK BROWN / NÂU SẪM!)"
    elif "Green" in name:
        x, y = 0.250, 0.15  # Swatch 3 Green bottom dark zone
        note = "Swatch 3 Green bottom dark zone (y=0.15 -> DARK FOREST / DEEP OLIVE GREEN!)"
    else:
        x, y = 0.060, 0.60  # Swatch 1/2 upper pastel area
        note = "Swatch 1/2 upper pastel area (y=0.60 -> SOFT DUSTY PASTEL PINK!)"

    print(f"{name:<30} RGB{str(rgb):<16} -> X={x:.3f}, Y={y:.2f} | {note}")
