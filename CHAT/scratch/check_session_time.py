import os
import time
from pathlib import Path

p = Path(r"d:\AI_Engineer\MSEMAX\session_data.json")
if p.exists():
    print("Size:", p.stat().st_size)
    print("Modified:", time.ctime(p.stat().st_mtime))
else:
    print("Does not exist")
