import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client import TransformClient

c = TransformClient(api_key=api_key, server_url="https://transform.unstructured.io")
j = c.jobs.get("0e0bbc06-828d-4f69-87c7-e92dbd95df73")
md = j.result.markdown

rows = re.findall(r"<tr>(.*?)</tr>", md, re.DOTALL)
print(f"Total rows found: {len(rows)}")

items = []
for i, r in enumerate(rows[:15]):
    cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", r, re.DOTALL)]
    print(f"Row {i}: {cells}")
