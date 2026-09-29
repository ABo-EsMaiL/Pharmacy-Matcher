with open(r'd:\AI_Engineer\Pharmacy-agy-vision\desktop_app\templates\index.html', encoding='utf-8') as f:
    lines = f.readlines()

screen_ranges = [
    ('screen-results', 1611, 1691),
    ('screen-history', 1692, 1707),
    ('screen-settings', 1708, 1809),
    ('screen-logs', 1810, 1827),
    ('screen-servers', 1828, 1983)
]

for name, start, end in screen_ranges:
    print(f"=== {name} (lines {start}-{end}) ===")
    for idx in range(start-1, min(start+15, end)):
        print(f"  {idx+1}: {lines[idx].strip()[:90]}")
