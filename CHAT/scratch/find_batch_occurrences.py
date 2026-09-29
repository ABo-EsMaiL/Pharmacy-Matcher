import os

root = r'd:\AI_Engineer\Pharmacy-agy'
for dirpath, _, filenames in os.walk(root):
    if any(x in dirpath for x in ['.git', '__pycache__', 'chrome_profile', 'node_modules', '.venv']):
        continue
    for f in filenames:
        if f.endswith(('.py', '.json', '.html', '.js', '.md', '.bat')):
            p = os.path.join(dirpath, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    for idx, line in enumerate(fp, 1):
                        lower = line.lower()
                        if '75' in line:
                            print(f"[75] {p}:{idx}: {line.strip()[:100]}")
                        elif 'batch' in lower and ('chunk' in lower or 'size' in lower or 'batch_size' in lower or 'items' in lower):
                            print(f"[BATCH] {p}:{idx}: {line.strip()[:100]}")
            except Exception as e:
                pass
