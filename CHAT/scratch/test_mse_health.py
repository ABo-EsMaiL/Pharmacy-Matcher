import requests

try:
    r = requests.get('http://127.0.0.1:8000/health', timeout=5)
    print('Health status:', r.status_code)
    print('Health body:', r.text)
except Exception as e:
    print('Error connecting to MSEMAX:', e)
