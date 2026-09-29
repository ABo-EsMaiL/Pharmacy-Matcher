with open(r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\app.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if any(k in line.lower() for k in ["chat/completions", "image", "upload", "file_payload"]):
            print(f"Line {i+1}: {line.strip()[:100]}")
