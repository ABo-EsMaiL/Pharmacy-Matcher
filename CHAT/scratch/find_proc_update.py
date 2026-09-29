with open(r'd:\AI_Engineer\Pharmacy-agy-vision\desktop_app\templates\index.html', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'process_update' in line:
            print(f'Line {i+1}: {line.strip()[:100]}')
