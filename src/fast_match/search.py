from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from dataclasses import dataclass
from math import ceil
from collections import Counter
from functools import lru_cache
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein, OSA
from ..match.text_match import normalize_text
from .attributes import (numeric_evidence, compare_strength_values, norm_num, NUMBER, PACK,
                         COUNT_FORM, VOLUME, structured_scalar)
from .identity_symbols import symbolic_identity_views, RETRIEVAL_ONLY_DESCRIPTORS

PHARMA_STOPWORDS = {
    'mg', 'gm', 'g', 'mcg', 'ml', 'syrup', 'suspension', 'tablet', 'tablets',
    'capsule', 'capsules', 'cream', 'ointment', 'gel', 'drops', 'suppository',
    'suppositories', 'ampoule', 'ampoules', 'vial', 'vials', 'milk',
    'pack', 'packs', 'box', 'boxes', 'strip', 'strips', 'carton', 'cartons', 'bag', 'bags', 'price', 'egp',
    # forms
    'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'حبوب', 'شراب', 'شرب', 'معلق', 'سائل',
    'مرهم', 'كريم', 'جل', 'جيل', 'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال',
    'لبوس', 'لبوسة', 'لبوسه', 'تحاميل', 'اقماع', 'نقط', 'قطرة', 'قطره',
    'بخاخ', 'بخاخة', 'بخاخه', 'سبراي', 'فوار', 'اكياس', 'كيس',
    'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه', 'محلول', 'مس', 'دهان', 'فيلم', 'شريط', 'لبن', 'حليب',
    # units & numbers
    'مجم', 'جم', 'جرام', 'مل', 'مللي', 'ملل', 'لتر', 'ميكرو', 'علبه', 'علبة',
    'باكت', 'باكو', 'كرتونه', 'كرتونة', 'فلتر', 'مج',
    # routes of administration
    'بالفم', 'فموي', 'فمويه', 'فموية', 'وريدي', 'عضلي', 'موضعي',
    # trade metadata
    'س', 'ج', 'سعر', 'جديد', 'قديم', 'تاريخ', 'بعيد', 'قريب', 'صغير', 'كبير', 'وسط',
    'محلي', 'مستورد', 'خاص', 'نقدى', 'اجل', 'عادي', 'عادى', 'مركب',
    # release modifiers & abbreviations
    'اس', 'ار', 'ام', 'ال', 'ريتارد', 'كرونو'
}

FORM_GROUPS = {
    'tablet': {'اقراص', 'قرص', 'كبسول', 'كبسوله', 'كبسولات', 'حبوب', 'فيلم', 'اقراض', 'tablet', 'tablets', 'capsule', 'capsules'},
    'syrup': {'شراب', 'شرب', 'معلق', 'سائل', 'syrup', 'suspension'},
    'cream': {'كريم', 'cream'},
    'ointment': {'مرهم', 'دهان', 'ointment'},
    'gel': {'جل', 'جيل', 'gel'},
    'suppository': {'لبوس', 'لبوسه', 'لبوسة', 'تحاميل', 'اقماع', 'suppository', 'suppositories'},
    'injection': {'امبول', 'امبوله', 'امبولات', 'حقن', 'فيال', 'ampoule', 'ampoules', 'vial', 'vials'},
    'drops': {'نقط', 'قطرة', 'قطره', 'drops'},
    'spray': {'بخاخ', 'بخاخة', 'بخاخه', 'سبراي', 'اسبراي', 'spray'},
    'sachet': {'فوار', 'اكياس', 'كيس'},
    'wash': {'شامبو', 'غسول', 'صابون', 'صابونة', 'صابونه'},
    'topical_solution': {'مس', 'محلول', 'لوشن', 'لوسيون', 'lotion', 'solution'},
    'powder': {'بودره', 'بودرة', 'مسحوق', 'powder'},
}

# Generic descriptions produce retrieval hypotheses only. They are not aliases
# and are never removed from a supplied structured trade_name.
RETRIEVAL_DESCRIPTORS = {
    'مطهر', 'مرطب', 'ملين', 'تفتيح', 'مهبلي', 'جلد', 'اطفال', 'للاطفال',
    'كبار', 'للكبار', 'دش', 'برطمان', 'نانو',
    'antiseptic', 'moisturizer', 'laxative', 'vaginal', 'skin', 'children',
    'adult', 'adults', 'jar', 'nano',
}

def extract_form_groups(text: str) -> set[str]:
    text = _separate_combination_form(normalize_text(text).lower())
    text = re.sub(r'(\d+)', r' \1 ', str(text))
    text = re.sub(r'[^\w\s]', ' ', text)
    norm = normalize_text(text).lower()
    words = set(norm.split())
    return {name for name, group_words in FORM_GROUPS.items() if words & group_words}


def extract_form_group(text: str) -> str | None:
    groups = extract_form_groups(text)
    return next(iter(groups)) if len(groups) == 1 else None

@lru_cache(maxsize=8192)
def extract_brand_tokens(text: str) -> str:
    text = _separate_combination_form(numeric_evidence(text).identity_text)
    text = re.sub(r'(\d+(?:\.\d+)?)', r' \1 ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    norm = normalize_text(text).lower()
    forms = {normalize_text(w).lower() for group in FORM_GROUPS.values() for w in group}
    words = [w for w in norm.split() if w not in PHARMA_STOPWORDS and w not in forms]
    return " ".join(words)


def _separate_combination_form(text: str) -> str:
    forms = sorted({normalize_text(w).lower() for words in FORM_GROUPS.values() for w in words}, key=len, reverse=True)
    return re.sub(r'(?<!\w)(كو|بلس|بلاس|كومب)(' + '|'.join(map(re.escape, forms)) + r')(?=\W|\d|$)', r'\1 \2', text)

def normalize_for_search(text: str) -> str:
    """Use the same Unicode normalization as parsing and classification."""
    text = normalize_text(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Replace punctuation with spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@dataclass(frozen=True)
class NameEvidence:
    plausible: bool
    exact: bool
    score: float
    edits: int
    coverage: float
    reason: str = ''
    token_similarity: float = 0.0
    character_similarity: float = 0.0
    weighted_edits: float = 0.0


@lru_cache(maxsize=32768)
def compare_names(left: str, right: str) -> NameEvidence:
    """Compare entire extracted names; no suffix/partial/prefix shortcuts.

    Variant numbers remain in identity and are checked by the classifier. They
    cannot supply the alphabetic evidence that admits a candidate here.
    """
    left_words = [w for w in left.split() if not w.isdigit()]
    right_words = [w for w in right.split() if not w.isdigit()]
    a, b = ''.join(left_words), ''.join(right_words)
    if not a or not b or not any(c.isalpha() for c in a) or not any(c.isalpha() for c in b):
        return NameEvidence(False, False, 0.0, 0, 0.0, 'empty_meaningful_name')
    length = max(len(a), len(b))
    coverage = min(len(a), len(b)) / length
    # Compact comparison tolerates OCR spaces; sorted tokens tolerate ordering.
    alignments = [(a, b)]
    # Reordering whole tokens is admissible only with token-to-token evidence.
    # Sorting fragments before concatenation must not turn a different name
    # into an apparently small edit (e.g. a split prefix rotated to the end).
    def tokens_correspond():
        if len(left_words) != len(right_words) or len(left_words) < 2:
            return None
        remaining = list(right_words)
        aligned = []
        for word in sorted(left_words, key=len, reverse=True):
            best = max(remaining, key=lambda other: Levenshtein.normalized_similarity(word, other))
            if (min(len(word), len(best)) < 3 and word != best) or not compare_names(word, best).plausible:
                return None
            aligned.append((word, best))
            remaining.remove(best)
        return ''.join(x for x, _ in aligned), ''.join(y for _, y in aligned)
    token_alignment = tokens_correspond()
    if token_alignment:
        alignments.append(token_alignment)
    aligned_a, aligned_b = min(alignments, key=lambda pair: Levenshtein.distance(*pair))
    edits = Levenshtein.distance(aligned_a, aligned_b)
    # Dot-confusion is weaker evidence than Unicode equivalence. It can admit
    # an ambiguous candidate, never establish exact identity.
    weighted_edits = float(edits)
    for op, i, j in Levenshtein.editops(aligned_a, aligned_b):
        if op == 'replace' and any(aligned_a[i] in group and aligned_b[j] in group
                                   for group in ('بتث', 'جحخ', 'دذ', 'رز', 'سش', 'صض', 'طظ', 'عغ', 'فق')):
            weighted_edits -= .5
    # Adjacent transposition is one OCR edit, not two unrelated substitutions.
    weighted_edits = min(weighted_edits, float(OSA.distance(aligned_a, aligned_b)))
    # A nearby swapped pair has strong full-name evidence, including a single
    # intervening character. It remains non-exact and must be adjudicated.
    nearby_transposition = False
    if len(aligned_a) == len(aligned_b):
        different = [i for i, (x, y) in enumerate(zip(aligned_a, aligned_b)) if x != y]
        if (len(different) == 2 and different[1] - different[0] <= 2 and
                aligned_a[different[0]] == aligned_b[different[1]] and
                aligned_a[different[1]] == aligned_b[different[0]]):
            weighted_edits = min(weighted_edits, 1.0)
            nearby_transposition = True
    edit_score = 1 - weighted_edits / length
    token_score = fuzz.token_sort_ratio(' '.join(left_words), ' '.join(right_words)) / 100
    char_score = fuzz.ratio(aligned_a, aligned_b) / 100
    if nearby_transposition:
        char_score = max(char_score, edit_score)
    budget = 0 if min(len(a), len(b)) < 3 else min(3, ceil(length * .20))
    reason = ('insufficient_full_name_coverage' if coverage < .75 else
              'full_name_edit_budget_exceeded' if edits > budget else
              'weak_full_name_character_evidence' if edit_score < .70 or char_score < .70 else
              'full_name_evidence')
    plausible = reason == 'full_name_evidence'
    # TF-IDF cannot rescue failure of this full-name gate.
    score = .75 * edit_score + .25 * token_score
    return NameEvidence(plausible, left == right, score, edits, coverage, reason,
                        token_score, char_score, weighted_edits)


@lru_cache(maxsize=8192)
def retrieval_name_views(raw: str) -> tuple[str, ...]:
    """Full product-name hypotheses, retaining the original for adjudication.

    A slash after dosage information can introduce supplier metadata. This is
    only a retrieval hypothesis, not permission to discard unknown identity.
    No supplier/drug dictionaries or learned aliases are used.
    """
    strict = extract_brand_tokens(raw)
    views = [strict]
    normalized = normalize_text(raw).lower()
    price_spaced = re.sub(r'(?<!\w)سعر(?=جديد|قديم)', 'سعر ', normalized)
    if price_spaced != normalized:
        views.append(extract_brand_tokens(price_spaced))
    # Slash hypotheses come from text after dose masking, so concentration
    # denominators are never mistaken for supplier descriptions.
    head, separator, tail = numeric_evidence(normalized).identity_text.partition('/')
    protected = {'كو', 'بلس', 'بلاس', 'كومب', 'co', 'plus', 'comp', 'sr', 'xr', 'cr', 'forte'}
    if separator and not set(tail.split()) & protected and not re.fullmatch(r'\s*\d+\s*', tail):
        views.append(extract_brand_tokens(head))
    # A known form is also a boundary before usage/marketing descriptions.
    # This hypothesis remains uncertain, and never uses text after a slash.
    words = normalize_for_search(_separate_combination_form(
        numeric_evidence(normalized).identity_text.partition('/')[0])).split()
    forms_all = {normalize_text(w).lower() for group in FORM_GROUPS.values() for w in group}
    for i, word in enumerate(words):
        if word in forms_all:
            prefix = extract_brand_tokens(' '.join(words[:i]))
            if len(re.sub(r'\W|\d', '', prefix)) >= 4:
                views.append(prefix)
            break
    for view in tuple(views):
        words = view.split()
        cleaned = [w for w in words if w not in RETRIEVAL_DESCRIPTORS]
        if cleaned != words:
            views.append(' '.join(cleaned))
        # Arabic attached prepositions are separate grammatical tokens, not
        # aliases. Keep this optional and require a substantial remaining word.
        unclitic = [w[3:] if w.startswith('بال') and len(w) >= 7 else w for w in words]
        if unclitic != words:
            views.append(' '.join(unclitic))
        # Release abbreviations may be joined by OCR. This is an uncertain
        # view only; original identity/attributes still go to adjudication.
        release = [w for w in words if w not in {'اسار', 'اس', 'ار', 'sr', 'xr', 'cr'}]
        if release != words:
            views.append(' '.join(release))
    for view in tuple(views):
        words = view.split()
        # Inflected commercial qualifiers are not drug-name substitutions.
        cleaned = [w for w in words if w not in {'جديده', 'الجديد', 'الجديده', 'القديم', 'القديمه'}]
        if cleaned != words:
            views.append(' '.join(cleaned))
    forms = {normalize_text(w).lower() for words in FORM_GROUPS.values() for w in words if len(w) >= 4}
    for view in tuple(views):
        words = view.split()
        # Only a trailing form-like token with a substantial remaining name.
        # Keep this uncertain: the classifier still sees the original form.
        if len(words) >= 2 and len(''.join(words[:-1])) >= 4 and any(
                abs(len(words[-1]) - len(form)) <= 1 and
                Levenshtein.distance(words[-1], form) == 1 for form in forms):
            views.append(' '.join(words[:-1]))
    return tuple(dict.fromkeys(v for v in views if any(c.isalpha() for c in v)))


@lru_cache(maxsize=32768)
def _whole_token_extension(left: str, right: str) -> NameEvidence:
    """One complete name plus additional words can be a retrieval hypothesis.

    This does not license substring matches or deletion of mismatching words on
    both sides. Require substantial whole-name coverage and a complete token
    alignment on the shorter side; the original extensions remain for the LLM.
    """
    a = [w for w in left.split() if any(c.isalpha() for c in w)]
    b = [w for w in right.split() if any(c.isalpha() for c in w)]
    if len(a) > len(b):
        a, b = b, a
    if not a or len(a) == len(b) or len(b) - len(a) > 1:
        return compare_names('', '')
    remaining = list(b)
    aligned = []
    for word in sorted(a, key=len, reverse=True):
        other = max(remaining, key=lambda x: Levenshtein.normalized_similarity(word, x))
        ev = compare_names(word, other)
        if not ev.plausible or (len(word) < 5 and word != other):
            return compare_names('', '')
        aligned.append((word, other))
        remaining.remove(other)
    covered = sum(min(len(x), len(y)) for x, y in aligned)
    coverage = covered / max(sum(map(len, a)), sum(map(len, b)))
    if covered < 6 or coverage < .60:
        return compare_names('', '')
    return NameEvidence(True, False, coverage * .85, 0, coverage,
                        'whole_token_extension_requires_adjudication')


def compare_name_views(left: tuple[str, ...], right: tuple[str, ...]) -> NameEvidence:
    if not left or not right:
        return compare_names('', '')
    strict = compare_names(left[0], right[0])
    if strict.plausible:
        return strict
    alternatives = [compare_names(a, b) for a in left for b in right]
    best = max(alternatives, key=lambda e: (e.plausible, e.score))
    if best.plausible:
        return NameEvidence(True, False, best.score * .97, best.edits, best.coverage,
                            'contextual_name_view_requires_adjudication', best.token_similarity,
                            best.character_similarity, best.weighted_edits)
    return strict


def unified_item(value: str | dict) -> dict:
    """Common input contract for Vision, Excel and legacy raw-name callers.

    Keep source fields and raw text. Local parsing fills absent fields only;
    extraction/raw disagreements stay explicit, never silently reconciled.
    """
    if isinstance(value, dict) and value.get('_unified'):
        return value
    item = dict(value) if isinstance(value, dict) else {'item_name_raw': value}
    raw = item.get('item_name_raw', item.get('raw_name', item.get('name', '')))
    raw = str(raw or '')
    def field(key):
        text = item.get(key)
        if key in {'strength', 'volume'} and isinstance(text, (int, float)) and not isinstance(text, bool):
            text = str(text)
        if not isinstance(text, str) or text.strip().lower() in {'', 'unknown', 'none', 'null', 'n/a', 'غير معروف'}:
            return ''
        return text.strip()
    trade, strength, form = field('trade_name'), field('strength'), field('form')
    strength_scalar = structured_scalar(strength)
    volume = field('volume')
    volume_scalar = structured_scalar(volume)
    raw_numbers = numeric_evidence(raw)
    raw_forms = extract_form_groups(raw)
    warnings = []
    extracted_fields = {key: item[key] for key in ('trade_name', 'strength', 'form', 'package', 'volume') if key in item}
    if volume and (volume_scalar is None or volume_scalar[1] not in {'ml', 'l', ''}):
        warnings.append('uncertain_structured_volume')
    normalized_strength = norm_num(normalize_text(strength)).lower()
    # A Vision field label cannot turn plain package volume/tube mass into dose.
    package_strength = bool(strength and (
        re.fullmatch(rf'{NUMBER}\s*{VOLUME}', normalized_strength) or
        ((raw_forms & {'cream', 'ointment', 'gel'} or extract_form_groups(form) & {'cream', 'ointment', 'gel'})
         and re.fullmatch(rf'{NUMBER}\s*(?:g|gm|جم|جرام)', normalized_strength))))
    package_field = strength if package_strength else ''
    if package_strength:
        if strength_scalar and strength_scalar[1] in {'ml', 'l'}:
            warnings.append('structured_strength_contains_volume')
        strength = ''
    # A field containing only a form/quantity is not a product identity.
    trade_valid = bool(trade and any(c.isalpha() for c in trade) and
                       extract_brand_tokens(trade) and not numeric_evidence(trade).strengths)
    if trade and not trade_valid:
        warnings.append('unusable_structured_trade_name')
    if not trade_valid:
        trade = extract_brand_tokens(raw)
    values = numeric_evidence(strength).strengths if strength else raw_numbers.strengths
    if strength_scalar and strength_scalar[1] == '':
        # This is an explicitly labelled strength field, never a bare number
        # guessed from a product name. Keep its missing unit as provenance.
        values = (strength_scalar[0],)
    if strength and not values:
        warnings.append('uncertain_structured_strength')
        values = raw_numbers.strengths
    if strength and compare_strength_values(values, raw_numbers.strengths) == 'conflict':
        warnings.append('structured_raw_strength_disagreement')
    forms = ({form} if form in FORM_GROUPS else extract_form_groups(form)) if form else raw_forms
    if form and not forms:
        warnings.append('uncertain_structured_form')
        forms = raw_forms
    if form and raw_forms and forms != raw_forms:
        warnings.append('structured_raw_form_disagreement')
    if trade_valid:
        # Full structured name may appear inside a longer raw description.
        t = re.sub(r'\W', '', normalize_for_search(trade))
        r = re.sub(r'\W', '', normalize_for_search(raw))
        if r and t not in r and not compare_name_views((normalize_for_search(trade),), retrieval_name_views(raw)).plausible:
            warnings.append('structured_raw_name_disagreement')
    # Canonical local values explicitly carry their measurement unit for LLMs.
    local_strength = ' | '.join(v if v.endswith(('%', 'mg/ml')) else v + ' mg' for v in values)
    package = field('package') or package_field or ' ; '.join(m.group(0) for m in re.finditer(
        rf'{NUMBER}\s*(?:{PACK}|{COUNT_FORM}|{VOLUME})(?![a-z])|(?:{PACK})\s*{NUMBER}',
        normalize_text(raw).lower()))
    return {**item, '_unified': True, 'raw_name': raw, 'item_name_raw': raw, 'name': raw,
            'trade_name': trade or None, 'strength': strength or local_strength or None,
            'form': form or (next(iter(forms)) if len(forms) == 1 else None),
            'package': package or None, 'source_page': item.get('source_page'),
            'source_file': item.get('source_file', ''),
            'extracted_fields': extracted_fields,
            'field_sources': {'trade_name': 'structured' if trade_valid else 'local',
                             'strength': 'structured' if strength else 'local',
                             'form': 'structured' if form else 'local'},
            'attribute_warnings': warnings, '_strength_values': tuple(values),
            '_structured_strength_scalar': strength_scalar,
            '_structured_volume': volume_scalar,
            '_forms': tuple(sorted(forms)),
            'identity_views': retrieval_name_views(raw) if not trade_valid else (normalize_for_search(trade),),
            'retrieval_reference': {'full': normalize_for_search(raw),
                                    'spans_removed': normalize_for_search(raw_numbers.identity_text)}}


def item_payload(value: str | dict) -> dict:
    item = unified_item(value)
    return {key: item.get(key) for key in ('raw_name', 'trade_name', 'strength', 'form', 'volume',
            'package', 'source_file', 'source_page', 'field_sources', 'attribute_warnings', 'extracted_fields',
            'identity_views')}


def name_evidence(requested: str | dict, candidate: str | dict) -> NameEvidence:
    a, b = unified_item(requested), unified_item(candidate)
    def identity_only(text, item):
        if item['field_sources']['trade_name'] == 'local':
            return ' '.join(w for w in text.split() if w not in RETRIEVAL_DESCRIPTORS)
        return text
    def base_trade(item):
        text = normalize_for_search(item['trade_name'] or '')
        text = re.sub(r'(?<=[^\W\d_])(?=\d)', ' ', text)
        text = re.sub(r'\b(?:كو|بلس|بلاس|كومب|co|plus|comp)\b', ' ', text)
        text = re.sub(r'(?<=[\u0621-\u064a])(?:بلاس|بلس|كومب)(?=\W|$)', ' ', text)
        return identity_only(' '.join(text.split()), item)
    primary = compare_names(base_trade(a), base_trade(b))
    symbolic = _symbolic_name_evidence(a, b)
    if symbolic is not None:
        return symbolic
    if primary.plausible:
        if any(item['field_sources']['trade_name'] == 'local' and
               set(normalize_for_search(item['trade_name'] or '').split()) & RETRIEVAL_DESCRIPTORS
               for item in (a, b)):
            return NameEvidence(True, False, primary.score, primary.edits, primary.coverage,
                                'raw_name_fallback', primary.token_similarity,
                                primary.character_similarity, primary.weighted_edits)
        return primary
    # Mixed sources need cross-comparison too: a clean structured request can
    # match a raw-only warehouse hypothesis even when the request's raw text
    # contains unrelated commercial descriptions (and vice versa).
    def comparison_views(item):
        return tuple(dict.fromkeys(identity_only(v, item) for v in
                     (base_trade(item), *retrieval_name_views(item['raw_name'])) if v))
    fallback = compare_name_views(comparison_views(a), comparison_views(b))
    if fallback.plausible:
        return NameEvidence(True, False, fallback.score, fallback.edits, fallback.coverage,
                            'raw_name_fallback', fallback.token_similarity,
                            fallback.character_similarity, fallback.weighted_edits)
    # Extensions are uncertain evidence only, not a new canonical identity.
    def extension_views(item):
        # A supplier/secondary tail must not become a whole-token anchor.
        masked = numeric_evidence(item['raw_name']).identity_text
        if '/' in masked and item['field_sources']['trade_name'] == 'local':
            return tuple(identity_only(v, item) for v in retrieval_name_views(masked.partition('/')[0]))
        return comparison_views(item)
    for left in extension_views(a):
        for right in extension_views(b):
            extended = _whole_token_extension(left, right)
            if extended.plausible:
                return extended
    return primary


@lru_cache(maxsize=1)
def _symbolic_ignored_tokens() -> frozenset[str]:
    return frozenset(PHARMA_STOPWORDS | RETRIEVAL_DESCRIPTORS | RETRIEVAL_ONLY_DESCRIPTORS |
                     {normalize_text(w) for group in FORM_GROUPS.values() for w in group})


def _symbolic_name_evidence(a: dict, b: dict) -> NameEvidence | None:
    """Optional code/spoken-word views can retrieve, never establish MATCH."""
    ignored = _symbolic_ignored_tokens()
    def views(item):
        # Mask measured attributes first; never interpret supplier tails as names.
        raw = numeric_evidence(item['raw_name']).identity_text.partition('/')[0]
        sources = [raw]
        if item['field_sources']['trade_name'] == 'structured':
            sources.insert(0, item['trade_name'] or '')
        return tuple(v for source in sources for v in symbolic_identity_views(source, ignored))
    for left in views(a):
        for right in views(b):
            if not (left.changed or right.changed) or left.spelling == right.spelling:
                continue
            # Shared D/K/number tokens cannot rescue a weak product name.
            if not compare_names(left.anchor, right.anchor).plausible:
                continue
            evidence = compare_names(left.identity, right.identity)
            if evidence.plausible:
                return NameEvidence(True, False, evidence.score * .96, evidence.edits,
                                    evidence.coverage, 'symbolic_identity_requires_adjudication',
                                    evidence.token_similarity, evidence.character_similarity,
                                    evidence.weighted_edits)
    return None

class FastCandidateFinder:
    def __init__(self):
        # Character N-Grams (2 to 4 chars)
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        self.corpus = []
        self.original_names = []
        self.ids = []
        self.matrix = None
        self.product_names = []
        self.name_views = []
        self.last_diagnostics = {}

    def fit(self, warehouse_items: list[dict]):
        """
        warehouse_items: list of dicts with 'id' and 'name'
        """
        self.items = [unified_item(item) for item in warehouse_items]
        self.ids = [item["id"] for item in self.items]
        self.original_names = [item["raw_name"] for item in self.items]
        self.product_names = [item['trade_name'] or '' for item in self.items]
        self.name_views = [retrieval_name_views(name) for name in self.original_names]
        self.corpus = [normalize_for_search(name) for name in self.product_names]
        self.matrix = None
        
        if any(self.corpus):
            self.matrix = self.vectorizer.fit_transform(self.corpus)

    def search(self, query: str | dict, top_k: int = 6) -> list[dict]:
        """Return the plausible trade-name set, retaining all attribute variants.

        top_k remains accepted for older callers, but cannot truncate presence
        evidence. TF-IDF ranks admitted names only; attributes never gate them.
        """
        self.last_diagnostics = {'before_gate': len(self.corpus), 'after_gate': 0,
                                 'after_top_k': 0, 'rejected_reasons': {}}
        if not self.corpus:
            return []
            
        requested = unified_item(query)
        req_brand = requested['trade_name'] or ''
        q_norm = normalize_for_search(req_brand)
        sims = [0.0] * len(self.corpus)
        if self.matrix is not None and q_norm:
            q_vec = self.vectorizer.transform([q_norm])
            sims = cosine_similarity(q_vec, self.matrix).flatten()
        
        results = []
        rejected = Counter()
        # Gate before top-k so shared forms/packaging cannot crowd out a name.
        for idx, cand_brand in enumerate(self.product_names):
            score = float(sims[idx])
            cand_name = self.original_names[idx]
            evidence = name_evidence(requested, self.items[idx])
            if evidence.plausible:
                results.append({
                    **self.items[idx],
                    "id": self.ids[idx],
                    "name": cand_name,
                    "score": .9 * evidence.score + .1 * score,
                    "brand_sim": evidence.score * 100,
                    "name_edits": evidence.edits,
                    "name_coverage": evidence.coverage,
                    "name_evidence_reason": evidence.reason,
                })
            else:
                rejected[evidence.reason] += 1
        results.sort(key=lambda c: c['score'], reverse=True)
        self.last_diagnostics.update(after_gate=len(results), after_top_k=len(results),
                                     rejected_reasons=dict(rejected))
        return results
