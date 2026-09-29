import shutil
from pathlib import Path

root = Path(r"D:\AI_Engineer\Pharmacy-agy-vision")
dist = root / "dist_production"

if dist.exists():
    shutil.copy2(root / "desktop_app" / "backend.py", dist / "desktop_app" / "backend.py")
    shutil.copy2(root / "desktop_app" / "templates" / "index.html", dist / "desktop_app" / "templates" / "index.html")
    shutil.copy2(root / "desktop_app" / "server_manager.py", dist / "desktop_app" / "server_manager.py")
    if (root / "src" / "extract" / "gemini_vision_extractor.py").exists():
        (dist / "src" / "extract").mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / "src" / "extract" / "gemini_vision_extractor.py", dist / "src" / "extract" / "gemini_vision_extractor.py")
    if (root / "src" / "extract" / "file_handler.py").exists():
        (dist / "src" / "extract").mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / "src" / "extract" / "file_handler.py", dist / "src" / "extract" / "file_handler.py")
    if (root / "src" / "fast_match" / "coordinator.py").exists():
        (dist / "src" / "fast_match").mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / "src" / "fast_match" / "coordinator.py", dist / "src" / "fast_match" / "coordinator.py")
    if (root / "src" / "config.py").exists():
        shutil.copy2(root / "src" / "config.py", dist / "src" / "config.py")
    print("dist_production synced successfully!")
else:
    print("dist_production does not exist")
