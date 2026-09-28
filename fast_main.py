import argparse
import sys
from pathlib import Path

# Fix Windows Arabic output encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import load_config
from src.extract.file_handler import read_input_files
from src.fast_match.coordinator import FastCoordinator
from src.output.excel_writer import write_results_excel

def parse_args():
    parser = argparse.ArgumentParser(description="Pharmacy Drug Matching Pipeline (FAST ENGINE)")
    parser.add_argument("--shortages", nargs="+", required=True, help="Path(s) to shortage files (Excel/PDF)")
    parser.add_argument("--warehouses", nargs="+", required=True, help="Path(s) to warehouse files (Excel/PDF)")
    return parser.parse_args()

def main():
    args = parse_args()

    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return

    print("\n[Settings]")
    print(f"  Model: {getattr(config, 'local_model', 'gpt-4o-mini')} (via MSEMAX Local API)")
    print("  Engine: Fast Hybrid (TF-IDF + LLM)")
    
    shortages_paths = [Path(p) for p in args.shortages]
    warehouse_paths = [Path(p) for p in args.warehouses]

    print("\n" + "="*60)
    print("[*] Processing Shortages files")
    print("="*60)
    shortages_data = read_input_files(
        shortages_paths,
        role="shortages",
        vision_api_url=getattr(config, "vision_api_url", "http://127.0.0.1:8001/v1/chat/completions"),
        vision_api_key=getattr(config, "vision_api_key", ""),
        vision_model=getattr(config, "vision_model", "gemini-3.8-flash"),
    )
    
    all_shortages = []
    for file_items in shortages_data.values():
        all_shortages.extend(file_items)
    print(f"\n[*] Total shortage items: {len(all_shortages)}\n")

    print("="*60)
    print("[*] Processing Warehouse files")
    print("="*60)
    warehouse_data = read_input_files(
        warehouse_paths,
        role="warehouse",
        vision_api_url=getattr(config, "vision_api_url", "http://127.0.0.1:8001/v1/chat/completions"),
        vision_api_key=getattr(config, "vision_api_key", ""),
        vision_model=getattr(config, "vision_model", "gemini-3.8-flash"),
    )

    # Fast Match Phase
    coordinator = FastCoordinator(config)
    results = coordinator.process(all_shortages, warehouse_data)

    # Output Phase
    output_path = Path("output/results_fast.xlsx")
    output_path.parent.mkdir(exist_ok=True)
    write_results_excel(results, output_path)

    print(f"\n✅ Finished! Results saved to: {output_path.absolute()}")

if __name__ == "__main__":
    main()
