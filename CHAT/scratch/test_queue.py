import sys
import json
import time
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")

from desktop_app.backend import API
from desktop_app.database import HistoryDB

def test_queue_and_auto_start():
    print("=== Testing Queue & Auto-Start ===")
    api = API()
    
    executed_order = []
    
    # Mock _process_worker
    orig_worker = api._process_worker
    def mock_worker(process_id, shortage_paths, warehouse_paths, is_restart=False):
        print(f"-> Worker executing for: {process_id}")
        executed_order.append(process_id)
        time.sleep(0.3)
        # Call finally block manually or simulate worker logic
        try:
            api.add_log(f"Mock done {process_id}")
        finally:
            with api._worker_lock:
                if api._process_queue:
                    next_id, next_s, next_w = api._process_queue.pop(0)
                    print(f"Triggering queued: {next_id}")
                    api._db.update_process(next_id, status='processing')
                    api._worker_thread = threading.Thread(
                        target=mock_worker,
                        args=(next_id, next_s, next_w, False),
                        daemon=True
                    )
                    api._worker_thread.start()
                else:
                    api._worker_thread = None

    api._process_worker = mock_worker
    
    # Start first process
    res1 = api.start_process("[]", "[]")
    id1 = res1["process_id"]
    print("Started process 1:", id1, "Queued:", res1["queued"])
    assert res1["queued"] is False
    
    # Immediately enqueue second process
    res2 = api.start_process("[]", "[]")
    id2 = res2["process_id"]
    print("Started process 2:", id2, "Queued:", res2["queued"])
    assert res2["queued"] is True
    assert res2["position"] == 1
    
    # Wait for both to finish
    time.sleep(1.2)
    
    print("Executed order:", executed_order)
    assert executed_order == [id1, id2], f"Expected [{id1}, {id2}], got {executed_order}"
    
    # Check DB status
    p1 = api._db.get_process(id1)
    p2 = api._db.get_process(id2)
    print(f"P1 status: {p1['status']}, P2 status: {p2['status']}")
    
    # Clean up test DB records
    api._db.delete_process(id1)
    api._db.delete_process(id2)
    print("Queue Auto-Start Test PASSED!")

if __name__ == "__main__":
    test_queue_and_auto_start()
