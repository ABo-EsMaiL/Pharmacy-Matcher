import requests
import re

r = requests.get("https://transform.unstructured.io/")
print("Status code:", r.status_code)
# Find JS script tags
scripts = re.findall(r'src=["\']([^"\']+\.js)["\']', r.text)
print("Scripts found:", scripts[:10])

# Download the main script and search for 'Recent files' or '/upload' or 'available for'
for s in scripts:
    if not s.startswith("http"):
        s_url = "https://transform.unstructured.io" + (s if s.startswith("/") else "/" + s)
    else:
        s_url = s
    try:
        js_text = requests.get(s_url, timeout=5).text
        if "Recent files" in js_text or "Recent Files" in js_text or "Available for" in js_text or "file_id" in js_text:
            print(f"Match in {s_url}")
            # Find relevant snippets
            matches = re.findall(r'.{0,100}(?:Recent files|Available for|/upload|/api/v2/).{0,100}', js_text, re.IGNORECASE)
            for m in matches[:10]:
                print("   ->", m)
    except Exception as e:
        pass
