import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(r"D:\AI_Engineer\Pharmacy-agy")
sys.path.insert(0, str(PROJECT_ROOT))

from desktop_app.backend import API

def test_api():
    api = API()
    print("1. Servers info:")
    print(api.get_servers_info())
    
    print("\n2. Initial Server logs:")
    print(api.get_server_logs())
    
    print("\n3. Testing stopped GAISTudio (port 8001):")
    res = api.test_server_instance("gaistudio")
    print("Result:", res)
    assert res.get("is_stopped") == True
    assert "متوقف" in res.get("error", "")
    
    print("\n4. Server logs after test:")
    logs = api.get_server_logs()
    print(logs)
    
    print("\n5. Testing clear server logs:")
    api.clear_server_logs()
    print("Cleared logs:", api.get_server_logs())
    assert api.get_server_logs() == "[]"
    
    print("\nALL VERIFICATIONS PASSED!")

if __name__ == "__main__":
    test_api()
