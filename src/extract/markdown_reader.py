"""
Markdown reader module - robustly reads and extracts drug items from Markdown files (.md).
Supports Markdown tables and bulleted / numbered lists.
"""

from pathlib import Path
import re


def read_markdown_file(filepath: Path) -> list[dict]:
    """
    Reads a Markdown file and extracts drug product items.
    
    Returns:
        list of dicts: [{"item_name_raw": str, "source_page": 1, "source_file": str}]
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Markdown file not found: {filepath}")

    print(f"  -> Reading Markdown file: {filepath.name}")

    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()

    items = []

    # 1. Try parsing Markdown Tables first
    table_items = _parse_markdown_tables(content, filepath.name)
    if table_items:
        print(f"  -> Extracted {len(table_items)} items from Markdown tables.")
        return table_items

    # 2. Try parsing Markdown lists (bullet / numbered)
    list_items = _parse_markdown_lists(content, filepath.name)
    if list_items:
        print(f"  -> Extracted {len(list_items)} items from Markdown list.")
        return list_items

    # 3. Fallback: treat non-empty, non-header lines as items
    fallback_items = _parse_fallback_lines(content, filepath.name)
    print(f"  -> Extracted {len(fallback_items)} items via line fallback.")
    return fallback_items


def _parse_markdown_tables(content: str, filename: str) -> list[dict]:
    """Extracts rows from markdown tables with auto-detected drug name column."""
    lines = [line.strip() for line in content.splitlines()]
    table_blocks = []
    current_table = []

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            current_table.append(line)
        else:
            if len(current_table) >= 2:
                table_blocks.append(current_table)
            current_table = []
    if len(current_table) >= 2:
        table_blocks.append(current_table)

    if not table_blocks:
        return []

    items = []
    keywords = ["صنف", "اسم", "دواء", "البيان", "item", "name", "product", "drug", "description"]
    arabic_pattern = re.compile(r"[\u0600-\u06FF]")

    for table in table_blocks:
        if len(table) < 2:
            continue

        raw_header = [c.strip() for c in table[0].split("|")[1:-1]]
        data_rows = []
        for row_str in table[1:]:
            # Skip separator line like |---|---|
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", row_str):
                continue
            cells = [c.strip() for c in row_str.split("|")[1:-1]]
            if any(cells):
                data_rows.append(cells)

        if not data_rows:
            continue

        # Detect best name column
        best_col_idx = 0
        best_score = -1

        for idx, h in enumerate(raw_header):
            score = 0
            h_lower = h.lower()
            if any(kw in h_lower for kw in keywords):
                score += 50
            if any(neg in h_lower for neg in ["رقم", "كود", "code", "id", "price", "سعر", "كمية", "qty"]):
                score -= 40

            sample_vals = [r[idx] for r in data_rows[:10] if idx < len(r) and r[idx]]
            if sample_vals:
                avg_len = sum(len(v) for v in sample_vals) / len(sample_vals)
                score += min(avg_len, 25)
                arabic_count = sum(1 for v in sample_vals if arabic_pattern.search(v))
                if arabic_count > 0:
                    score += (arabic_count / len(sample_vals)) * 20

            if score > best_score:
                best_score = score
                best_col_idx = idx

        for r_idx, row in enumerate(data_rows, start=1):
            if best_col_idx < len(row):
                val = row[best_col_idx].strip()
                # Clean markdown links or bolding if present
                val = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", val)
                val = re.sub(r"[*_~`]", "", val).strip()
                if val and len(val) >= 2 and not val.isdigit():
                    items.append({
                        "item_name_raw": val,
                        "source_page": 1,
                        "source_file": filename,
                        "source_row": r_idx
                    })

    return items


def _parse_markdown_lists(content: str, filename: str) -> list[dict]:
    """Extracts items from markdown bulleted or numbered lists."""
    items = []
    lines = content.splitlines()

    list_pattern = re.compile(r"^(?:[\*\-\+]|\d+[\.\)])\s+(.*)$")

    for idx, line in enumerate(lines, start=1):
        line_clean = line.strip()
        match = list_pattern.match(line_clean)
        if match:
            raw_text = match.group(1).strip()
            # Clean formatting: [link](url), **bold**, `code`
            raw_text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", raw_text)
            raw_text = re.sub(r"[*_~`]", "", raw_text).strip()

            # Split off common quantity or price suffixes if delineated by colon, dash, or tab
            # e.g., "Panadol Extra 24 Tab - 5 boxes" -> "Panadol Extra 24 Tab"
            parts = re.split(r"\s+[-:–—|]\s+", raw_text)
            candidate = parts[0].strip() if parts else raw_text
            if candidate and len(candidate) >= 2 and not candidate.isdigit():
                items.append({
                    "item_name_raw": candidate,
                    "source_page": 1,
                    "source_file": filename,
                    "source_row": idx
                })

    return items


def _parse_fallback_lines(content: str, filename: str) -> list[dict]:
    """Extracts non-empty plain lines that are not headers or code fences."""
    items = []
    in_codeblock = False

    for idx, line in enumerate(content.splitlines(), start=1):
        clean = line.strip()
        if clean.startswith("```"):
            in_codeblock = not in_codeblock
            continue
        if in_codeblock or not clean or clean.startswith("#"):
            continue

        clean_text = re.sub(r"[*_~`]", "", clean).strip()
        if len(clean_text) >= 2 and not clean_text.isdigit():
            items.append({
                "item_name_raw": clean_text,
                "source_page": 1,
                "source_file": filename,
                "source_row": idx
            })

    return items
