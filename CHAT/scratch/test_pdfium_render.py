import pypdfium2 as pdfium
from pathlib import Path
import time
import os

pdf_path = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-015\input_warehouses\المكرومي المنصورة.pdf")
pdf = pdfium.PdfDocument(pdf_path)
print(f"Loaded {pdf_path.name}: {len(pdf)} pages")

t0 = time.time()
page = pdf[0] # Page 1

# Render at 2x scale (~144 dpi) and 2.5x scale (~180 dpi)
for scale in [2.0, 2.5]:
    image = page.render(scale=scale).to_pil()
    
    # Save as JPEG with quality 85
    jpg_path = Path(f"C:/Users/kakak/.gemini/antigravity/brain/916274de-7f92-49fc-a0a8-d291664b474a/scratch/test_page1_scale{scale}.jpg")
    image.save(jpg_path, format="JPEG", quality=85, optimize=True)
    jpg_size_kb = os.path.getsize(jpg_path) / 1024
    
    # Save as WebP with quality 85
    webp_path = Path(f"C:/Users/kakak/.gemini/antigravity/brain/916274de-7f92-49fc-a0a8-d291664b474a/scratch/test_page1_scale{scale}.webp")
    image.save(webp_path, format="WEBP", quality=85)
    webp_size_kb = os.path.getsize(webp_path) / 1024
    
    print(f"Scale {scale}x ({image.width}x{image.height}): JPEG={jpg_size_kb:.1f} KB | WebP={webp_size_kb:.1f} KB")

t1 = time.time()
print(f"Rendering took: {t1 - t0:.2f}s")
