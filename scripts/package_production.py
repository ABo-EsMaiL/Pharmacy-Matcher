"""
Production Packaging Script for Pharmacy Matcher.
Creates a clean, ready-to-deploy distribution folder for the pharmacy client machine.
Excludes all development caches, test databases, scratch scripts, and temporary inputs.
"""

import os
import shutil
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist_production"

def package():
    print("=" * 60)
    print("[*] Packaging Pharmacy Matcher for Production Deployment")
    print("=" * 60)

    if DIST_DIR.exists():
        print(f"[-] Removing existing {DIST_DIR.name}...")
        shutil.rmtree(DIST_DIR)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy desktop_app
    print("[+] Copying desktop_app/ ...")
    shutil.copytree(
        PROJECT_ROOT / "desktop_app",
        DIST_DIR / "desktop_app",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
    )

    # 2. Copy src
    print("[+] Copying src/ ...")
    shutil.copytree(
        PROJECT_ROOT / "src",
        DIST_DIR / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
    )

    # 2.5 Copy scripts (like free_ports.bat)
    print("[+] Copying scripts/ ...")
    (DIST_DIR / "scripts").mkdir(exist_ok=True)
    if (PROJECT_ROOT / "scripts" / "free_ports.bat").exists():
        shutil.copy2(PROJECT_ROOT / "scripts" / "free_ports.bat", DIST_DIR / "scripts" / "free_ports.bat")

    # 3. Copy root essential files
    essential_files = [
        "requirements.txt",
        ".env.example",
        "fast_main.py",
    ]
    for filename in essential_files:
        src_file = PROJECT_ROOT / filename
        if src_file.exists():
            print(f"[+] Copying {filename} ...")
            shutil.copy2(src_file, DIST_DIR / filename)

    # 4. Create fresh data directory structure with clean database
    data_dir = DIST_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "processes").mkdir(exist_ok=True)
    (data_dir / "inputs").mkdir(exist_ok=True)
    (data_dir / ".unstructured_cache").mkdir(exist_ok=True)
    
    # Initialize fresh history.db in dist
    db_path = data_dir / "history.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shortage_files TEXT,
            warehouse_files TEXT,
            total_shortages INTEGER DEFAULT 0,
            matched_count INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            not_found_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'processing',
            output_file TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[+] Initialized clean history.db in data/")

    # Default production settings.json
    settings_json = data_dir / "settings.json"
    settings_json.write_text('{\n  "local_api_url": "http://127.0.0.1:8000/v1/chat/completions",\n  "gemini_model": "gemini-2.5-flash",\n  "match_threshold": 0.75,\n  "msemax_dir": ""\n}', encoding="utf-8")
    print("[+] Created default settings.json")

    # 5. Create run_app.bat in root of dist
    run_bat_content = """@echo off
chcp 65001 > nul
title Pharmacy Matcher - فارما ماتش

echo ========================================================
echo    تشغيل برنامج فارما ماتش (Pharmacy Matcher)
echo ========================================================
echo.

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python غير مثبت على هذا الجهاز!
    echo يرجى تثبيت Python 3.10 أو أحدث من https://www.python.org/
    echo وتأكد من تحديد خيار "Add Python to PATH" أثناء التثبيت.
    echo.
    pause
    exit /b 1
)

:: Check if virtual environment exists, if not create one
if not exist "venv\\Scripts\\activate.bat" (
    echo [*] جاري إنشاء البيئة الافتراضية لأول مرة (venv)...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    echo [*] جاري تثبيت الحزم المطلوبة من requirements.txt...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\\Scripts\\activate.bat
)

:: Check if .env exists, if not copy from .env.example
if not exist ".env" (
    if exist ".env.example" (
        echo [*] إنشاء ملف الإعدادات .env من النموذج...
        copy .env.example .env > nul
    )
)

echo [*] جاري تشغيل واجهة البرنامج...
python desktop_app\\app.py

if %errorlevel% neq 0 (
    echo.
    echo [!] حدث خطأ أثناء تشغيل البرنامج.
    pause
)
"""
    (DIST_DIR / "run_app.bat").write_text(run_bat_content, encoding="utf-8")
    print("[+] Created run_app.bat launcher")

    # 6. Create README_SETUP.md in Arabic
    readme_content = """# دليل تثبيت وتشغيل برنامج "فارما ماتش" على جهاز العميل / الصيدلية

أهلاً بك! هذا المجلد يحتوي على النسخة الجاهزة للتشغيل (Production) لبرنامج مطابقة نواقص الصيدليات مع كشوف المخازن.

---

## الخطوة 1: متطلبات التشغيل الأساسية (لمرة واحدة فقط)
1. **تثبيت Python**:
   - قم بتحميل وتثبيت **Python (الإصدار 3.10 أو 3.11 أو 3.12)** من الموقع الرسمي: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - ⚠️ **هام جداً أثناء التثبيت**: ضع علامة صح على خيار **"Add python.exe to PATH"** في أسفل نافذة التثبيت الأولى.

2. **(اختياري) متصفح الويب WebView2**:
   - نظام Windows 10 و 11 يحتوي على Microsoft Edge WebView2 مثبتاً مسبقاً بشكل افتراضي، وهو ما يعتمد عليه البرنامج لعرض الواجهة الحديثة.

---

## الخطوة 2: تشغيل البرنامج
- ببساطة، اضغط ضغطتين مزدوجتين (Double Click) على ملف:
  👉 **`run_app.bat`**

- **في المرة الأولى فقط**: سيقوم الملف تلقائياً بإنشاء بيئة العمل وتثبيت المكتبات المطلوبة (قد يستغرق 1 - 2 دقيقة حسب سرعة الإنترنت).
- **في المرات التالية**: سيفتح البرنامج فوراً في ثوانٍ معدودة.

---

## الخطوة 3: إعداد مفاتيح الـ API (إذا لزم)
- يحتوي المجلد على ملف اسمه `.env` (أو قم بنسخ `.env.example` إلى `.env`).
- افتح ملف `.env` بأي محرر نصوص (مثل المفكرة Notepad) وضع المفاتيح الخاصة بك:
  ```env
  UNSTRUCTURED_API_KEY=مفتاح_الموقع
  GEMINI_API_KEY=مفتاح_جيميني_إذا_كنت_تستخدمه
  ```
- أو يمكنك إدخال وتعديل الإعدادات ورابط السيرفر المحلي مباشرة من شاشة **"إعدادات النظام"** داخل البرنامج نفسه.

---

## مكونات المجلد:
- `desktop_app/`: ملفات الواجهة الرسومية وسطح المكتب.
- `src/`: محرك المطابقة الذكي ومعالجة الإكسيل وملفات الـ PDF.
- `data/`: مجلد حفظ العمليات والنتائج وقاعدة البيانات (يبدأ نظيفاً وخالياً).
- `run_app.bat`: زر التشغيل السريع للبرنامج.
"""
    (DIST_DIR / "README_SETUP.md").write_text(readme_content, encoding="utf-8")
    print("[+] Created README_SETUP.md")

    print("\n" + "=" * 60)
    print(f"[SUCCESS] Production package successfully created at:\n  {DIST_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    package()
