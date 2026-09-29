import requests
import json

r = requests.get('http://127.0.0.1:8001/debug/state').json()
for t in r.get('turns', []):
    print(f"--- Turn {t.get('index')} ---")
    print("Tag:", t.get('tag'))
    print("Cls:", t.get('cls'))
    print("Role:", t.get('role'))
    print("Author elements:", t.get('author_elements'))
    print("Preview:\n", repr(t.get('preview')))
