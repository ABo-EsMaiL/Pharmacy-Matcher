from pathlib import Path

p = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-004\input_warehouses\جملة العمروووو.pdf")
cdir = p.parent.parent.parent / 'data' / '.unstructured_cache'
print("Calculated cache dir:", cdir)
print("Exists:", cdir.exists())
if cdir.exists():
    for f in cdir.glob("*"):
        print("  -", f.name, f.stat().st_size)
