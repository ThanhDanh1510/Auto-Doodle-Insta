import colorsys

# Move Green X coordinate slightly RIGHT from 0.250 to 0.295:
# X = 0.295, Y = 0.15 -> Moves right towards Yellow/Ochre zone -> WARM MOSS GREEN (Xanh rêu đẫm)!

colors = [
    ("Moss Green Stamen", (77, 69, 36)),
]

print("MOSS GREEN SHIFT RIGHT TEST:")
print("=" * 80)

for name, rgb in colors:
    x, y = 0.295, 0.15  # Shift right from 0.250 to 0.295
    note = "Shifted RIGHT (x=0.295, y=0.15) -> WARM DEEP MOSS GREEN (Xanh rêu đẫm!)"
    print(f"{name:<25} RGB{str(rgb):<16} -> X={x:.3f}, Y={y:.2f} | {note}")
