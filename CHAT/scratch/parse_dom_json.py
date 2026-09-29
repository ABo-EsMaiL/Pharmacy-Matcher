import re
import json
import html

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\user_raw_dom.txt", "r", encoding="utf-8") as f:
    html_content = f.read()

# Extract code blocks using regex
code_raw_blocks = re.findall(r'<code[^>]*>(.*?)</code>', html_content, re.DOTALL)
print(f"Found {len(code_raw_blocks)} <code> blocks in HTML.")

gemini_extracted_items = []

for i, cb in enumerate(code_raw_blocks):
    text = html.unescape(re.sub(r'<[^>]+>', '', cb)).strip()
    if '"items":' in text or '"item_name_raw":' in text:
        print(f"\n--- Code block {i+1} has JSON! Length: {len(text)} ---")
        try:
            # try to parse json directly
            data = json.loads(text)
            items = data.get("items", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            print(f"Successfully parsed JSON in block {i+1}! Items count: {len(items)}")
            gemini_extracted_items.extend(items)
        except Exception as e:
            print(f"JSON direct parse failed in block {i+1}: {e}. Trying regex extraction...")
            # regex extract {"item_name_raw": "...", "source_page": ...}
            matches = re.findall(r'\{\s*"item_name_raw":\s*"([^"]+)"(?:,\s*"source_page":\s*(\d+))?\s*\}', text)
            print(f"Regex extracted {len(matches)} items from block {i+1}!")
            for m in matches:
                gemini_extracted_items.append({
                    "item_name_raw": m[0],
                    "source_page": int(m[1]) if m[1] else i + 1
                })

print(f"\nTotal Gemini extracted items from DOM: {len(gemini_extracted_items)}")

# If no <code> blocks or partial, let's also search using regex across the entire html_content
if len(gemini_extracted_items) == 0:
    print("Searching entire HTML via regex...")
    matches = re.findall(r'\{\s*\\?"item_name_raw\\?":\s*\\?"([^\\"]+)\\"(?:,\s*\\?"source_page\\?":\s*(\d+))?\s*\}', html_content)
    print(f"Regex across full HTML found {len(matches)} items.")
    for m in matches:
        gemini_extracted_items.append({
            "item_name_raw": m[0],
            "source_page": int(m[1]) if m[1] else 1
        })

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\gemini_dom_items.json", "w", encoding="utf-8") as out:
    json.dump(gemini_extracted_items, out, ensure_ascii=False, indent=2)
print("Saved to scratch/gemini_dom_items.json")
