target_file = r"d:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py"
with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "- Drops (نقط, قطرة) ONLY match Drops." in l:
        lines[i] = l.replace(
            "- Drops (نقط, قطرة) ONLY match Drops.",
            "- Drops (نقط, قطرة) ONLY match Drops. NEVER match drops with tablets or plain numbers without drops (e.g. كتافلام نقط does NOT match كتافلام 50)."
        )
        print("Updated line", i+1)
        break

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(lines)
