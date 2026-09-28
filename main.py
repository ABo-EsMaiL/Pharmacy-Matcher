"""Pharmacy Drug Matching Pipeline

Matches shortages with warehouse inventory using Gemini API.
Outputs an Excel file with the results.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import load_config
from src.extract.file_handler import read_input_files
from src.match.coordinator import Coordinator
from src.output.excel_writer import write_results_excel


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Match drug shortages against warehouse catalogs",
    )
    parser.add_argument(
        "--shortages", "-s",
        nargs="+",
        type=Path,
        required=True,
        help="Shortages files (Excel or PDF)",
    )
    parser.add_argument(
        "--warehouses", "-w",
        nargs="+",
        type=Path,
        required=True,
        help="Warehouse files (Excel or PDF or JSON)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("output/results.xlsx"),
        help="Output Excel file path (default: output/results.xlsx)",
    )

    args = parser.parse_args()

    for f in args.shortages + args.warehouses:
        if not f.exists():
            parser.error(f"File not found: {f}")

    try:
        config = load_config()
    except ValueError as e:
        print(f"[!] {e}")
        print("Please copy .env.example to .env and fill in the keys.")
        return 1

    print(f"\n[Settings]")
    print(f"  Model: {config.gemini_model}")
    print(f"  Unstructured API: {'OK' if config.unstructured_api_key else 'Missing'}")
    print(f"  Gemini API: {'OK' if config.gemini_api_key else 'Missing'}")

    shortage_data = read_input_files(
        args.shortages, role="shortages", api_key=config.unstructured_api_key,
    )

    all_shortages = []
    for filename, items in shortage_data.items():
        all_shortages.extend(items)

    if not all_shortages:
        print("[!] No items found in shortages files!")
        return 1

    print(f"\n[*] Total shortage items: {len(all_shortages)}")

    warehouse_data = read_input_files(
        args.warehouses, role="warehouse", api_key=config.unstructured_api_key,
    )

    if not warehouse_data:
        print("[!] No items found in warehouse files!")
        return 1

    coordinator = Coordinator(config)
    results = coordinator.process(all_shortages, warehouse_data)

    write_results_excel(results, args.output)

    print(f"\n[+] Finished!")
    print(f"    Results saved to: {args.output.resolve()}")

    summary = results.get("summary", {})
    if summary.get("not_found_count", 0) > 0:
        print(f"    [!] {summary['not_found_count']} items NOT found in any warehouse")
    if summary.get("review_count", 0) > 0:
        print(f"    [*] {summary['review_count']} items require manual review")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
