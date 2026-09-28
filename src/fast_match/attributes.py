"""Numeric evidence shared by retrieval, classification and final validation.

Only numbers with dose evidence are removed from product identity. Packaging,
volume and price spans are removed separately; remaining numbers are variants.
"""
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
import re

from ..match.text_match import normalize_text

NUMBER = r"(?:\d+(?:\.\d+)?|\.\d+)"
MASS = r"(?:ميكروجرام|مكجم|مجم|جرام|mcg|mg|gm|µg|μg|مج|جم|g)"
VOLUME = r"(?:ملليلتر|مللي|ملل|مل|ml|لتر|litre|liter|l)"
PACK = r"(?:باكت|باكو|باكيت|كرتونه|علبه|عبوه|شريط|شرائط|strips?|packs?|boxes?|box|cartons?|bags?)"
COUNT_FORM = r"(?:اقراص|قرص|كبسولات|كبسوله|كبسول|امبولات|امبوله|امبول|فيال|اكياس|tablets?|capsules?|ampoules?|vials?)"
DOSE_FORM = r"(?:لبوس|تحاميل|اقماع|اقراص|كبسول|شراب|معلق|نقط|حقن|suppositor(?:y|ies)|syrup|tablets?|capsules?)"


def norm_num(text: str) -> str:
    text = str(text).translate(str.maketrans(
        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    text = text.replace("٫", ".")
    return re.sub(r"(?<=\d)[,،](?=\d)", ".", text)


def _decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


def structured_scalar(value) -> tuple[str, str] | None:
    """Normalize spelling of a single structured value without inventing units.

    An empty unit remains empty. This helper does not parse product names or
    infer dosage, concentration, package size, or a unit from medical knowledge.
    """
    if isinstance(value, bool) or value is None:
        return None
    text = norm_num(normalize_text(str(value))).lower().strip()
    match = re.fullmatch(rf'({NUMBER})\s*({MASS}|{VOLUME}|[%٪])?', text)
    if not match:
        return None
    unit = match[2] or ''
    groups = {'mg': {'mg', 'مجم', 'مج'}, 'g': {'g', 'gm', 'جم', 'جرام'},
              'mcg': {'mcg', 'µg', 'μg', 'مكجم', 'ميكروجرام'},
              'ml': {'ml', 'مل', 'مللي', 'ملل', 'ملليلتر'},
              'l': {'l', 'litre', 'liter', 'لتر'}, '%': {'%', '٪'}}
    unit = next((key for key, words in groups.items() if unit in words), unit)
    return _decimal(Decimal(match[1])), unit


def structured_attribute_uncertainty(left: dict, right: dict) -> str | None:
    """Keep explicit structured volumes and missing measurement bases cautious."""
    a, b = left.get('_structured_volume'), right.get('_structured_volume')
    if a or b:
        if not a or not b or not a[1] or not b[1]:
            return 'structured_volume_uncertain'
        if a != b:
            return 'structured_volume_difference'
    for item, other in ((left, right), (right, left)):
        scalar = item.get('_structured_strength_scalar')
        if scalar and scalar[1] == '':
            counterpart = other.get('_structured_strength_scalar')
            if counterpart is None:
                # Consult written raw units, not a mass converted to mg by the
                # legacy parser: unitless 500 is not proof of 0.5 g.
                atoms = re.findall(rf'{NUMBER}\s*{MASS}(?![a-z\u0600-\u06ff])',
                                   norm_num(normalize_text(other['raw_name'])).lower())
                counterpart = structured_scalar(atoms[0]) if len(atoms) == 1 else None
            if counterpart and counterpart[1] not in {'', 'mg'}:
                return 'structured_strength_unit_unspecified'
    return None


@dataclass(frozen=True)
class NumericEvidence:
    strengths: tuple[str, ...]
    identity_text: str


@lru_cache(maxsize=32768)
def numeric_evidence(raw: str) -> NumericEvidence:
    text = norm_num(normalize_text(raw)).lower()
    # Expose attached, explicitly labelled counts only. Splitting every digit
    # here would turn a name/variant before drops into a guessed bare dose.
    text = re.sub(rf'(?<=[^\W\d_])(?={NUMBER}\s*(?:{PACK}|{COUNT_FORM})(?![a-z]))', ' ', text)
    remaining = list(text)
    occupied = set()
    strengths = []

    def mask(start, end):
        occupied.update(range(start, end))
        remaining[start:end] = " " * (end - start)

    def available(match):
        return not any(i in occupied for i in range(*match.span()))

    # Explicit commercial context takes precedence over bare-number heuristics.
    for pattern in (
        rf"(?:{PACK})\s*[:x×-]?\s*{NUMBER}",
        rf"(?<![\w.]){NUMBER}\s*(?:{PACK}|{COUNT_FORM})(?![a-z])",
        rf"(?:سعر(?:\s+(?:جديد|قديم))?|price|س\s*[./]?\s*ج)\s*[:=]?\s*{NUMBER}",
        rf"(?<![\w.]){NUMBER}\s*(?:جنيه|egp|س\s*\.?\s*ج)(?!\w)",
    ):
        for match in re.finditer(pattern, text):
            if available(match):
                # Retain the dosage-form word; remove the count, not its form.
                mask(*match.span())

    topical = bool(re.search(r"(?:كريم|مرهم|جيل|جل|cream|ointment|gel)", text))
    mass_pattern = rf"(?<![\d.])(?P<values>{NUMBER}(?:\s*/\s*{NUMBER})*)\s*(?P<unit>{MASS})(?![a-z\u0600-\u06ff])(?:\s*/\s*(?P<den>{NUMBER})?\s*(?P<volume>{VOLUME})(?![a-z\u0600-\u06ff]))?"
    for match in re.finditer(mass_pattern, text):
        if not available(match):
            continue
        unit = match['unit']
        grams = unit in {'جم', 'جرام', 'gm', 'g'}
        # A standalone gram amount on a topical tube is package mass.
        if topical and grams and not match['volume']:
            mask(*match.span())
            continue
        factor = Decimal('0.001') if unit in {'mcg', 'µg', 'μg', 'مكجم', 'ميكروجرام'} else Decimal(1000) if grams else Decimal(1)
        values = [Decimal(v.strip()) * factor for v in match['values'].split('/')]
        if match['volume']:
            denominator = Decimal(match['den'] or '1')
            if match['volume'] in {'لتر', 'liter', 'litre', 'l'}:
                denominator *= 1000
            if denominator <= 0:
                continue
            strengths.append('/'.join(_decimal(v / denominator) for v in values) + 'mg/ml')
        else:
            strengths.append('/'.join(_decimal(v) for v in values))
        mask(*match.span())

    for match in re.finditer(rf"(?<![\d.])({NUMBER})\s*[%٪]", text):
        if available(match):
            strengths.append(_decimal(Decimal(match[1])) + '%')
            mask(*match.span())

    # Standalone ml is volume, never concentration. Ratios were consumed above.
    for match in re.finditer(rf"(?<![\d.]){NUMBER}\s*{VOLUME}(?![a-z\u0600-\u06ff])", text):
        if available(match):
            mask(*match.span())

    # Unitless ratios are explicit multi-strength evidence (e.g. 875/125).
    for match in re.finditer(rf"(?<![\w.]){NUMBER}(?:\s*/\s*{NUMBER})+(?![\d.])", text):
        if available(match):
            strengths.append('/'.join(_decimal(Decimal(v.strip())) for v in match[0].split('/')))
            mask(*match.span())

    # Attached dosage notation must survive: 25لبوس. Unlabelled product numbers
    # are retained as identity, not guessed doses.
    for match in re.finditer(rf"(?<![\w.])({NUMBER})\s*(?={DOSE_FORM}(?:\W|\d|$))", text):
        if available(match):
            strengths.append(_decimal(Decimal(match[1])))
            mask(*match.span())

    for match in re.finditer(r"(?<!\w)(ربع|نص|نصف)(?!\w)", text):
        if available(match):
            strengths.append('0.25' if match[1] == 'ربع' else '0.5')
            mask(*match.span())

    # A dose immediately followed by a count (500mg20 tablets) exposes a new
    # boundary after dose masking. Counts cannot become product variants.
    for pattern in (
        rf"(?<![\w.]){NUMBER}\s*(?:{PACK}|{COUNT_FORM})(?![a-z])",
        rf"-\s*{NUMBER}\s*ب(?=\W|$)",
    ):
        for match in re.finditer(pattern, ''.join(remaining)):
            mask(*match.span())

    return NumericEvidence(tuple(strengths), ''.join(remaining))


def get_strength_pattern(text: str) -> str | None:
    strengths = numeric_evidence(text).strengths
    return '|'.join(strengths) if strengths else None


def compare_strengths(left: str, right: str) -> str:
    """Compare like measurements; missing volume cannot prove a conflict.

    A total mass and a mass/volume concentration need a shared volume basis.
    Unequal values on the same basis remain explicit conflicts.
    """
    return compare_strength_values(numeric_evidence(left).strengths, numeric_evidence(right).strengths)


def compare_strength_values(a, b) -> str:
    """Compare parsed fields without treating a missing value as a conflict."""
    if not a or not b:
        return 'missing'
    if a == b:
        return 'compatible'
    def basis(value):
        return 'mass_per_volume' if value.endswith('mg/ml') else 'percent' if value.endswith('%') else 'mass'
    # Compare every available like-for-like field before declaring uncertainty.
    for kind in ('mass', 'mass_per_volume', 'percent'):
        av = tuple(v for v in a if basis(v) == kind)
        bv = tuple(v for v in b if basis(v) == kind)
        if av and bv and av != bv:
            return 'conflict'
    return 'incomparable'
