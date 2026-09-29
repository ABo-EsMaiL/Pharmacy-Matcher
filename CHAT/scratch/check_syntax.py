import ast
import sys

files = [
    r"D:\AI_Engineer\MSEMAX-GAIStudio-vision\app.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\src\extract\gemini_vision_extractor.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\src\fast_match\coordinator.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\desktop_app\backend.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\dist_production\src\extract\gemini_vision_extractor.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\dist_production\src\fast_match\coordinator.py",
    r"D:\AI_Engineer\Pharmacy-agy-vision\dist_production\desktop_app\backend.py",
]

errors = 0
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            ast.parse(fp.read())
        print(f"[OK] {f}")
    except Exception as e:
        print(f"[FAIL] {f}: {e}")
        errors += 1

if errors == 0:
    print("\nALL FILES VALID SYNTAX!")
else:
    sys.exit(1)
