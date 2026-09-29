from pathlib import Path

file_path = Path(r"D:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py")
lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

new_lines = []
inserted = False
for line in lines:
    new_lines.append(line)
    if "Sprays (بخاخ, سبراي) ONLY match Sprays." in line and not inserted:
        # Detect line ending
        ending = "\r\n" if line.endswith("\r\n") else "\n"
        new_lines.append(f"   - LIQUIDS VS SOLID STRENGTHS (Syrups vs Plain mg):{ending}")
        new_lines.append(f"     - Liquid dosage forms (شراب, معلق, نقط) are formulated by volume (مل) or concentration per dose (/5مل). Plain numeric strengths (like 400mg, 500mg, 1000mg) without \"/5ml\" or \"شراب\" or \"مل\" signify solid tablets/capsules.{ending}")
        new_lines.append(f"     - If one side explicitly specifies a syrup (شراب), it MUST NEVER match a candidate that specifies a plain tablet strength (like 400مجم, 500مجم) without the word \"شراب\" or \"مل\" or \"/5مل\". This is a strict form conflict -> return \"status\": \"no_match\".{ending}")
        inserted = True

if inserted:
    file_path.write_text("".join(new_lines), encoding="utf-8")
    print("[SUCCESS] Inserted Liquids vs Solid rule into SYSTEM_PROMPT.")
else:
    print("[!] Line not found.")
