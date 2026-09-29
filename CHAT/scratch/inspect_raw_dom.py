with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\user_raw_dom.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("Total text length:", len(text))
pos1 = text.find("turn-C0BFD868")
pos2 = text.find("turn-16668AE7")
print("Turn 1 pos:", pos1)
print("Turn 2 pos:", pos2)
if pos2 != -1:
    print("Turn 2 text tail:\n", text[pos2:pos2+1000])
