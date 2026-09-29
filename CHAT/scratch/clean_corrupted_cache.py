from pathlib import Path
import shutil

p = Path("data/processes/PROC-017/cache")
if p.exists():
    shutil.rmtree(p)
    print("Cleaned corrupted PROC-017 cache successfully")
else:
    print("No cache to clean")
