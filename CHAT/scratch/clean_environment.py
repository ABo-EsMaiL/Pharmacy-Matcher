import os
import glob
import shutil
import sqlite3
from pathlib import Path

# 1. Delete transform-result-*.json in root
for f in glob.glob("transform-result-*.json"):
    try:
        os.remove(f)
        print(f"Deleted {f}")
    except Exception as e:
        print(f"Error removing {f}: {e}")

# 2. Clear processes in data/history.db
db_path = Path("data/history.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM processes")
    conn.commit()
    conn.close()
    print("Cleared history.db processes")

# 3. Clean data/processes
proc_dir = Path("data/processes")
if proc_dir.exists():
    for item in proc_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
            print(f"Removed directory {item}")
        else:
            try:
                item.unlink()
                print(f"Removed file {item}")
            except Exception as e:
                print(f"Error deleting file {item}: {e}")

print("Cleanup completed successfully.")
