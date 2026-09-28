"""
وحدة الإعدادات - تحميل مفاتيح API والإعدادات من ملف .env
Configuration module - loads API keys and settings from .env file.
"""

from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import os


def gateway_api_key() -> str:
    """Local gateway credential; keep the value outside version control."""
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
    return os.getenv('MSEMAX_API_KEY', '').strip()


@dataclass
class Config:
    """إعدادات المشروع الرئيسية."""

    # مفاتيح API المطلوبة
    unstructured_api_key: str
    gemini_api_key: str

    # إعدادات Unstructured API
    unstructured_base_url: str = "https://transform.unstructured.io"

    # إعدادات MSEMAX (Local API)
    local_api_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    local_api_key: str = gateway_api_key()
    local_model: str = "gpt-4o-mini" # or gpt-4o depending on what the wrapper defaults to

    # Vision Gateway (MSEMAX-GAIStudio-vision)
    vision_api_url: str = "http://127.0.0.1:8001/v1/chat/completions"
    vision_api_key: str = gateway_api_key()
    vision_model: str = "gemini-3.8-flash"

    # إعدادات Gemini (لم تعد مستخدمة حاليا)
    gemini_model: str = "gemini-3.6-flash"
    match_threshold: float = 0.75


def load_config(env_path: Path | None = None) -> Config:
    """
    تحميل الإعدادات من متغيرات البيئة (أو ملف .env).

    Args:
        env_path: مسار ملف .env (اختياري). إذا لم يُحدَّد يبحث في المجلد الحالي.

    Returns:
        كائن Config يحتوي على جميع الإعدادات.
    """
    # تحميل متغيرات البيئة من ملف .env
    if env_path:
        load_dotenv(env_path)
    else:
        # البحث عن .env في جذر المشروع
        project_root = Path(__file__).resolve().parent.parent
        load_dotenv(project_root / ".env")

    # قراءة المفاتيح (اختيارية للمحرك البصري الجديد)
    unstructured_key = os.getenv("UNSTRUCTURED_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    vision_url = os.getenv("VISION_API_URL", "http://127.0.0.1:8001/v1/chat/completions").strip()
    vision_key = os.getenv("VISION_API_KEY", gateway_api_key()).strip()
    vision_model = os.getenv("VISION_MODEL", "gemini-3.8-flash").strip()

    return Config(
        unstructured_api_key=unstructured_key,
        gemini_api_key=gemini_key,
        vision_api_url=vision_url,
        vision_api_key=vision_key,
        vision_model=vision_model,
    )
