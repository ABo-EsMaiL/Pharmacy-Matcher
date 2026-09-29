from rapidfuzz import fuzz

def check_al(r, w):
    has_al_r = r.startswith('ال')
    has_al_w = w.startswith('ال')
    if has_al_r != has_al_w:
        r_strip = r[2:] if has_al_r else r
        w_strip = w[2:] if has_al_w else w
        if fuzz.ratio(r_strip, w_strip) < 75:
            return 'BLOCKED'
    return 'PASSED'

tests = [
    ('ابيكوتيل', 'البوتيل'),
    ('بنادول', 'البنادول'),
    ('كتافلام', 'الكتفلام'),
    ('فيوسيدل', 'فيوسيدين'),
    ('ميبو', 'ميو'),
    ('جرانتريل', 'جرانتيل')
]
for r, w in tests:
    print(f'{r} vs {w} -> {check_al(r, w)}')
