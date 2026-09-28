"""Language-level spelling hypotheses, never canonical product aliases.

Only whole tokens are interpreted. An independent alphabetic name anchor must
still pass the normal full-name gate; shared letter/number codes cannot admit
unrelated products. Original fields and numeric attribute parsing are untouched.
"""
import re
from dataclasses import dataclass
from functools import lru_cache

from ..match.text_match import normalize_text
from .attributes import norm_num


# Generic spoken digits and English letter names, not pharmaceutical mappings.
# Ambiguous transliterations are deliberately only hypotheses for adjudication.
_DIGITS = (
    ('zero', 'زيرو', 'صفر'), ('one', 'وان', 'واحد'),
    ('two', 'تو', 'اثنين', 'اتنين'), ('three', 'ثري', 'ثلاثه', 'تلاته'),
    ('four', 'فور', 'اربعه'), ('five', 'فايف', 'خمسه'),
    ('six', 'سكس', 'سته'), ('seven', 'سفن', 'سبعه'),
    ('eight', 'ايت', 'ثمانيه', 'تمانيه'), ('nine', 'ناين', 'تسعه'),
)
_LETTERS = {
    'a': ('ايه',), 'b': ('بي',), 'c': ('سي',), 'd': ('دي', 'د'),
    'e': ('اي',), 'f': ('اف',), 'g': ('جي',), 'h': ('اتش',),
    'i': ('آي',), 'j': ('جاي',), 'k': ('كي', 'كيه', 'ك'),
    'l': ('ال',), 'm': ('ام',), 'n': ('ان',), 'o': ('او',),
    'p': ('پي',), 'q': ('كيو',), 'r': ('ار',), 's': ('اس',),
    't': ('تي',), 'u': ('يو',), 'v': ('في', 'ڤي'), 'w': ('دبليو',),
    'x': ('اكس',), 'y': ('واي',), 'z': ('زد', 'زيد'),
}
NUMBER_WORDS = {normalize_text(w): str(n) for n, words in enumerate(_DIGITS) for w in words}
# NFKC/Arabic normalization can make two spoken letters indistinguishable.
# Keep the alternatives rather than silently claiming a unique transliteration.
LETTER_WORDS = {}
for letter, words in _LETTERS.items():
    for word in words:
        key = normalize_text(word)
        LETTER_WORDS.setdefault(key, set()).add(letter)
LETTER_WORDS = {key: tuple(sorted(value)) for key, value in LETTER_WORDS.items()}

RETRIEVAL_ONLY_DESCRIPTORS = frozenset({'ميكروفيلم', 'لزقه', 'microfilm', 'patch', 'patches'})


@dataclass(frozen=True)
class SymbolicView:
    identity: str
    anchor: str
    spelling: str
    changed: bool


@lru_cache(maxsize=8192)
def symbolic_identity_views(text: str, ignored: frozenset[str]) -> tuple[SymbolicView, ...]:
    normalized = norm_num(normalize_text(text)).lower()
    # This spelling retains alphanumeric attachment for uncertainty tracking.
    spelling = re.sub(r'[^\w\s.]', ' ', normalized)
    split = re.sub(r'(?<=[^\W\d_])(?=\d)|(?<=\d)(?=[^\W\d_])', ' ', spelling)
    # Keep newly removed descriptors in the spelling signature so their removal
    # cannot be mistaken for deterministic equality.
    original = [w for w in spelling.split() if w not in ignored or w in RETRIEVAL_ONLY_DESCRIPTORS]
    tokens = [w for w in split.split() if w not in ignored or w in LETTER_WORDS or w in NUMBER_WORDS]
    anchors = [w for w in tokens if w not in LETTER_WORDS and w not in NUMBER_WORDS
               and any(c.isalpha() for c in w) and not re.fullmatch('[a-z]', w)]
    # Codes, forms and packaging cannot supply a product-name anchor.
    if not anchors or len(''.join(anchors)) < 3:
        return ()
    variants = [()]
    for token in tokens:
        choices = LETTER_WORDS.get(token, (NUMBER_WORDS.get(token, token),))
        variants = [(*prefix, word) for prefix in variants for word in choices][:16]
    original_spelling = ' '.join(original)
    return tuple(SymbolicView(' '.join(words), ' '.join(anchors), original_spelling,
                              ' '.join(words) != original_spelling)
                 for words in variants)
