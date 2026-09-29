import re

def extract_strengths(text: str) -> list[str]:
    # Normalize indicators and eastern digits first
    t = str(text)
    # Remove dates, pack counts like 20قرص, 3شريط, 30كيس
    t = re.sub(r'\d+\s*(قرص|اقراص|كبسول|شريط|امبول|كيس|فلتر|علبه|ملل?|سم)', '', t)
    # Match patterns like 4/30, 12.5/5, 1000, 500, 250, 457, 642, 0.25, 2.5
    matches = re.findall(r'(?:\d+(?:\.\d+)?(?:\/\d+(?:\.\d+)?)*)\s*(?:مجم|جم|مج|gm|mg)', t)
    if not matches:
        # try without unit if preceding or followed by number
        pass
    return matches

for s in ["زانوجليد4/30اقراص س ج", "زانوچيلد 4 مج اقراص/باكت 60", "فلوموكس 500 كبسول", "فلوموكس 1000 اقراص"]:
    print(s, "->", extract_strengths(s))
