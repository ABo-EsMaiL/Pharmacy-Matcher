import sys
import os

gaistudio_dir = r"D:\AI_Engineer\MSEMAX-GAIStudio"
sys.path.insert(0, gaistudio_dir)

try:
    import fastapi
    import uvicorn
    import playwright
    print("[OK] FastAPI, Uvicorn, Playwright imported successfully.")
except Exception as e:
    print(f"[FAIL] Import error: {e}")

# Check if port 8001 is listening
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex(('127.0.0.1', 8001))
s.close()
if result == 0:
    print("[PORT 8001] is OPEN and LISTENING!")
else:
    print("[PORT 8001] is NOT listening.")
