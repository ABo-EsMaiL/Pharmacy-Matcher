with open(r'd:\AI_Engineer\Pharmacy-agy-vision\desktop_app\templates\index.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'process_complete' in line or 'viewProcess' in line or 'loadResults' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
