for mod in ['fitz', 'pdf2image', 'pypdf', 'pdfplumber', 'PIL', 'cv2', 'playwright', 'fastapi', 'uvicorn', 'requests']:
    try:
        __import__(mod)
        print(f"{mod}: available")
    except ImportError:
        print(f"{mod}: NOT available")
