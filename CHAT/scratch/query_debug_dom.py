import requests

try:
    r = requests.get('http://127.0.0.1:8001/debug_dom', timeout=5)
    print("Status:", r.status_code)
    print("Data keys:", list(r.json().keys()))
    print("URL:", r.json().get('url'))
    print("Title:", r.json().get('title'))
    print("Buttons count:", r.json().get('buttonsCount'))
    print("Keywords:", r.json().get('modelKeywords'))
except Exception as e:
    print('Error:', e)
