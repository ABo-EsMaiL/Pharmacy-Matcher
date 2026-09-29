import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(r"D:\AI_Engineer\Pharmacy-agy")
sys.path.insert(0, str(PROJECT_ROOT))

from desktop_app.server_manager import MultiServerManager

def main():
    print("Testing MultiServerManager with ChatGPT...")
    mgr = MultiServerManager(settings={}, logger_callback=print)
    
    # 1. Start
    res = mgr.start("chatgpt")
    print("Start result:", res)
    
    # 2. Check running
    running = False
    for i in range(8):
        time.sleep(0.5)
        if mgr.is_running("chatgpt"):
            running = True
            print(f"Server listening after {(i+1)*0.5}s")
            break
            
    print("is_running:", running)
    
    # 3. Test ping
    status = mgr.get_all_status("chatgpt")
    print("Server status:", status.get("chatgpt"))
    
    # 4. Stop
    stop_res = mgr.stop("chatgpt")
    print("Stop result:", stop_res)
    
    print("Post-stop is_running:", mgr.is_running("chatgpt"))

if __name__ == "__main__":
    main()
