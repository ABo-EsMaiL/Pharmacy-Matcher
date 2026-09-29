import base64
import json
import time
from pathlib import Path
import pypdfium2 as pdfium
import requests

# 1. إعداد المسارات والملف
PDF_PATH = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-015\input_warehouses\المكرومي المنصورة.pdf")
ENDPOINT_URL = "http://127.0.0.1:8001/v1/chat/completions"
API_KEY = "[REDACTED_CREDENTIAL]"

print(f"[*] جاري قراءة ملف: {PDF_PATH.name}")
pdf = pdfium.PdfDocument(PDF_PATH)
page_1 = pdf[0]

# 2. تحويل الصفحة 1 إلى صورة عالية الجودة وصغيرة الحجم (WebP)
print("[*] تحويل الصفحة الأولى إلى صورة WebP عالية الدقة...")
image = page_1.render(scale=2.5).to_pil()
temp_img_path = Path("temp_page1_test.webp")
image.save(temp_img_path, format="WEBP", quality=85)
print(f"[+] تم إنشاء الصورة: {temp_img_path.name} (الحجم: {temp_img_path.stat().st_size / 1024:.1f} KB)")

# 3. تحويل الصورة إلى Base64
with open(temp_img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# 4. الـ Prompt الصارم المنظم للاستخراج
prompt_text = (
    "أنت خبير صيدلي متخصص في استخراج وتحليل بيانات فواتير وقوائم الأدوية.\n"
    "قم باستخراج جميع الأدوية والمنتجات الطبية الموجودة في هذه الصورة بدقة صيدلانية كاملة.\n"
    "القواعد الصارمة:\n"
    "1. استخرج كل صنف أو سطر منتج دوائي يظهر في الصورة كعنصر مستقل.\n"
    "2. (item_name_raw): انقل اسم الصنف كاملاً كما هو في الفاتورة بالحرف دون أي تعديل أو اختصار مع الاحتفاظ بالاسم والتركيز والهيئة الدوائية والشركة.\n"
    "3. (trade_name): الاسم التجاري الصافي للدواء فقط بدون التركيز أو الهيئة الدوائية (مثال: دوليبرين، كيتولاك، كونكور، اوجمنتين).\n"
    "4. (strength): تركيز الدواء كما هو مكتوب في الصورة (مثال: 1000 مجم، 500 mg، 1 جم، 20/40) أو اتركه فارغاً إذا لم يذكر.\n"
    "5. (form): الهيئة الدوائية (أقراص، كبسول، شراب، حقن، أمبول، نقط، كريم، مرهم، جل، بخاخ...) أو اتركها فارغة إذا لم تذكر.\n"
    "6. تجنب تصحيح الأخطاء الإملائية أو ترجمة الكلمات أو تغيير الأرقام. لا تُدرج أسعار أو كميات أو خصومات أو أرقام أكواد.\n"
    "7. الحروف باللغة العربية والإنجليزية السليمة فقط.\n"
    "8. الرد يجب أن يكون كائن JSON صالح فقط بدون أي نصوص تمهيدية:\n"
    "{\n"
    '  "items": [\n'
    "    {\n"
    '      "item_name_raw": "الاسم المكتوب كاملاً بالتركيز والهيئة كما هو",\n'
    '      "trade_name": "الاسم التجاري فقط",\n'
    '      "strength": "التركيز",\n'
    '      "form": "الهيئة",\n'
    '      "source_page": 1\n'
    "    }\n"
    "  ]\n"
    "}"
)

# 5. تجهيز الـ Payload
payload = {
    "model": "gemini-3.8-flash",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/webp;base64,{img_b64}"
                    }
                }
            ]
        }
    ],
    "stream": False
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"[*] إرسال الطلب إلى الـ Endpoint ({ENDPOINT_URL})...")
print("    راقب الآن نافذة المتصفح المفتوحة أمامك لترى هل استلم الصورة والبرومبت!")

t0 = time.time()
try:
    resp = requests.post(ENDPOINT_URL, json=payload, headers=headers, timeout=180)
    print(f"[+] Response Status: {resp.status_code} (استغرق {time.time() - t0:.1f} ثانية)")
    
    if resp.status_code == 200:
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        print("\n=== الرد المستلم من الـ Endpoint ===")
        print(content[:500] + "...\n(باقي الرد تم استلامه بنجاح)")
    else:
        print(f"[!] خطأ من الـ Gateway: {resp.status_code}")
        print(resp.text)
except Exception as e:
    print(f"[!] فشل الاتصال بالـ Endpoint: {e}")