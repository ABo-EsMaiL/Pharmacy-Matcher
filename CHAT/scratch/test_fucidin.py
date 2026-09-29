from rapidfuzz import fuzz
print('فيوسيدل vs فيوسيدين:', fuzz.ratio('فيوسيدل', 'فيوسيدين'))
print('ميبو vs ميو:', fuzz.ratio('ميبو', 'ميو'))
