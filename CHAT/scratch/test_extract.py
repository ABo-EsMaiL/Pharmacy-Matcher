import base64
import json
import os
import sys

sys.path.append(r"D:\AI_Engineer\MSEMAX-GAIStudio-vision")
from app import extract_prompt_and_images, ChatMessage

payload = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract these items"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/webp;base64,UklGRkAAAABXRUJQVlA4IDQAAADwAQCdASoBAAEAAQAcJaACdLoB+AA/vlNAAP7/9f////////7///////9////////+/////"
                }
            }
        ]
    }
]

messages = [ChatMessage(**m) for m in payload]
prompt, images = extract_prompt_and_images(messages)
print("PROMPT:", prompt)
print("IMAGES:", images)
for img in images:
    print(f"Exists: {os.path.exists(img)}, Size: {os.path.getsize(img)}")
