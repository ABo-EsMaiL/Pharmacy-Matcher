import re

with open(r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
keywords = ["timeout", "button", "stream", "send", "chat", "generation", "stop", "disabled", "status"]

for i, line in enumerate(lines):
    lower = line.lower()
    for kw in ["timeout", "stop", "cancel", "run", "stream", "disabled", "generate"]:
        if kw in lower and ("button" in lower or "wait" in lower or "poll" in lower or "timeout" in lower or "aria" in lower):
            print(f"Line {i+1}: {line.strip()[:100]}")
            break
