target_file = r"d:\AI_Engineer\Pharmacy-agy\src\fast_match\coordinator.py"
with open(target_file, "r", encoding="utf-8") as f:
    text = f.read()

old_s = r"slash_req = re.search(r'\b(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)\b', shortage_name)"
new_s = r"slash_req = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', shortage_name)"

old_w = r"slash_wh = re.search(r'\b(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)\b', warehouse_item)"
new_w = r"slash_wh = re.search(r'(?:^|[^\d/])(\d+(?:\.\d+)?\/\d+(?:\.\d+)?)(?:[^\d/]|$)', warehouse_item)"

assert old_s in text, "old_s not found"
assert old_w in text, "old_w not found"

text = text.replace(old_s, new_s).replace(old_w, new_w)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated slash regex in coordinator.py.")
