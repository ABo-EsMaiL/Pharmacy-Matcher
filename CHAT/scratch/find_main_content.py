with open(r'd:\AI_Engineer\Pharmacy-agy-vision\desktop_app\templates\index.html', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if '.main-content' in line or 'main-content' in line:
            print(f'Line {i+1}: {line.strip()[:100]}')
        if '.screen' in line:
            print(f'Screen Line {i+1}: {line.strip()[:100]}')
        if 'action-bar-bottom' in line:
            print(f'Action Bar Line {i+1}: {line.strip()[:100]}')
