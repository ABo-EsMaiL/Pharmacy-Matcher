import re

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\last_dom_snippet.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("Searching for file inputs or buttons:")
for m in re.finditer(r'<input[^>]+>', text, re.IGNORECASE):
    print("INPUT:", m.group(0))

for m in re.finditer(r'<button[^>]+aria-label=[^>]+>', text, re.IGNORECASE):
    print("BUTTON:", m.group(0)[:120])
