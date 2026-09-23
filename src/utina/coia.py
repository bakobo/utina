"""COIA v2 reference implementation.

The specification is README.md; the flag definitions are APPENDIX-D.md.
Public domain.

NOTE: contains Unicode string constants. Download rather than copy/paste from a
browser; check TATWEEL below renders as an Arabic elongation mark, not a Latin letter.
"""
import json
import os
import unicodedata as ud

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    """Expand a normative table of hex ranges into a set of codepoints."""
    spans = json.load(open(os.path.join(_HERE, "tables.json")))[name]
    out = set()
    for span in spans:
        lo, _, hi = span.partition("-")
        out.update(range(int(lo, 16), int(hi or lo, 16) + 1))
    return out


SPLIT = _load("split")          # -> word separator
VIRAMA = _load("virama")        # ccc == 9; licenses a following joiner
ARABIC = _load("arabic")        # Arabic-script blocks; licenses ZWNJ between letters

TATWEEL = 0x0640                # decorative elongation, not a letter
ZWJ, ZWNJ = 0x200D, 0x200C
FOLD = {0x02BC: 0x02BB}         # modifier apostrophe -> okina; no orthography differs
ME = None                       # the reflexive sentinel (distinct from "")

# Non-ASCII decimal digits are accepted on lookup and normalized on generation.
_DIGITS = {}
for _cp in range(0x110000):
    _d = ud.decimal(chr(_cp), None)
    if _d is not None:
        _DIGITS[chr(_cp)] = str(_d)

# Comma variants accepted when splitting flag groups on lookup. U+FF0C folds under
# NFKC already; these do not.
COMMA_VARIANTS = ",、،，"


def _joiner_ok(s, i):
    """RFC 5892 CONTEXTJ, with the Arabic clause approximated by script block."""
    cp = ord(s[i])
    if cp == ZWJ:
        return i > 0 and ord(s[i - 1]) in VIRAMA
    if cp == ZWNJ:
        if i > 0 and ord(s[i - 1]) in VIRAMA:
            return True
        return 0 < i < len(s) - 1 and ord(s[i - 1]) in ARABIC and ord(s[i + 1]) in ARABIC
    return False


def normalize(s):
    """Reduce a string to COIA canonical form.

    A separately conformant operation: matching is defined in terms of it, so every
    implementation exports it. Step order is normative.
    """
    s = ud.normalize("NFKC", s).casefold()
    out = []
    on_base = False             # may a combining mark attach here?
    for i, ch in enumerate(s):
        cp = ord(ch)
        cat = ud.category(ch)
        if cp in SPLIT:
            out.append(" ")
            on_base = False
        elif cp == TATWEEL:
            pass                # decorative
        elif cat == "Cf":
            if _joiner_ok(s, i):
                out.append(ch)  # orthographically required joiner
        elif cat in ("Mn", "Mc"):
            if on_base:
                out.append(ch)  # an orphaned mark has no base; drop it
        elif cat == "Me":
            pass                # enclosing marks are decorative (keycaps, circles)
        elif cat[0] in "LN":
            out.append(chr(FOLD.get(cp, cp)))
            on_base = True
        else:
            on_base = False
    return "-".join("".join(out).split())


# ---------------------------------------------------------------- localization
#
# There is ONE template, in every language: the three fields in the order
# who, role, scope, joined by spaces, with scope omitted when empty.
#
#     create_alias("en", "Cecilia", "CEO", "Acme")  ->  cecilia-ceo-acme
#     create_alias("ja", "田中太郎", "経理担当者", "三菱銀行")
#                                   ->  田中太郎-経理担当者-三菱銀行
#
# WHY THERE IS NOTHING TO LOCALIZE. Native-speaker review, 2026-08-25, 47
# independent reviews across 11 languages, one flagship model from each of 7 labs.
# Two findings
# collapsed the appendix that used to live here:
#
# 1. Bare apposition was proposed independently in EVERY language. A connector
#    is what forces a template to know things it cannot know -- grammatical
#    gender of an organization it has never seen, the case a preposition
#    governs, whether an article contracts, which allomorph a particle takes.
#    Drop the connector and every one of those problems is not solved but
#    dissolved. An alias is a business card, not a sentence, and a bare noun
#    sequence is the business-card register in all eleven.
# 2. The order is who-role-scope, unanimously, in 8 of the 11 (33 reviews, no
#    dissent) and in 35 of all 47. Only ja, ko and zh dissent, and they do not
#    agree with each other -- ja proposes scope-role-who, ko scope-who-role, zh
#    has no majority at all across 8 reviews while still putting who first in 5
#    of them. A 2-of-3 split that its own neighbours contradict is weak evidence
#    against 33 unanimous reviews.
#
# The cost is honest and small: ja and ko get an order their speakers rated
# second-best. Against that, the label is private, search is order-independent
# (see `matches`), and its only reader already knows what it means.
#
# WHAT USED TO BE HERE, so it is not rediscovered as a missing feature:
#   - Korean -(으)로서 allomorphy (로서 after a vowel or ㄹ, else 으로서). The rule
#     was CORRECT; a reviewer confirmed it against the examples. It went with the
#     particle it served.
#   - Russian в/во before certain consonant clusters. Already dead before this
#     change -- apposition had removed its only call site.
#   - Per-language connectors: en `as`/`at`, es `como`, de `als`, fr `comme`,
#     pt `como`, it `come`/`presso`, ru `как`, ja `の`/`として`/`での`, ar `بصفة`/`في`,
#     he `בתפקיד`/`ב`, zh `作为`/`在`.
# Reintroducing any of them means reintroducing a reason for a connector.

def template(who, role, scope):
    """The alias body, before normalization. Language-independent."""
    return f"{who} {role}" + (f" {scope}" if scope else "")


# The only per-language datum left. Consulted ONLY for a reflexive alias, i.e.
# when `who` is the ME sentinel; for every other alias `lang` selects nothing.
PRONOUNS = {
    "en": "me", "es": "yo", "de": "ich", "fr": "moi", "pt": "eu", "it": "io",
    "ru": "я", "ja": "私", "zh": "我", "ko": "나", "ar": "أنا", "he": "אני",
}

LANGUAGES = frozenset(PRONOUNS)


# ---------------------------------------------------------------------- flags

def _flag_group(digits, name):
    """Validate, fold to ASCII, deduplicate, sort descending."""
    if digits is None or digits == "":
        return ""
    seen = set()
    for ch in digits:
        d = _DIGITS.get(ch)
        if d is None:
            raise ValueError(f"{name} must contain only decimal digits, got {ch!r}")
        seen.add(d)
    return "".join(sorted(seen, reverse=True))


ASSIGNED = set("014567 89".replace(" ", ""))   # 2 and 3 are reserved


def create_alias(lang, who, role, scope="", flags="", private_flags=""):
    """Mint an alias. `who` may be the ME sentinel for a reflexive alias."""
    if lang not in PRONOUNS:
        raise ValueError(f"unsupported language {lang!r}; "
                         f"a generator must reject rather than fall back")
    reflexive = who is ME
    if reflexive:
        who = PRONOUNS[lang]

    flags = _flag_group(flags, "flags")
    private_flags = _flag_group(private_flags, "private_flags")
    for d in flags:
        if d not in ASSIGNED:
            raise ValueError(f"digit {d!r} is reserved; a generator must not emit it")
    if reflexive and ("0" in flags):
        raise ValueError("reflexive aliases must not carry flag 0")

    # Substitution is a single simultaneous pass: values are placed, never rescanned,
    # and never interpreted as replacement patterns.
    body = normalize(template(who, role, scope))

    # Preconditions are stated on NORMALIZED values, so role='.' is caught.
    if not normalize(role):
        raise ValueError("role must be non-empty after normalization")
    if not reflexive and not normalize(who):
        raise ValueError("who must be non-empty after normalization")
    if not body:
        raise ValueError("alias is empty after normalization")

    out = body
    if flags or private_flags:
        out += "," + flags
    if private_flags:
        out += "," + private_flags
    return out


def parse_alias(s):
    """Split a raw alias into (body, spec_flags, private_flags).

    Flag groups are stripped BEFORE the body is normalized; the reverse order
    destroys the delimiter. Comma variants are accepted here so a CJK or Arabic
    user retyping on their own keyboard is understood.
    """
    for v in COMMA_VARIANTS[1:]:
        s = s.replace(v, ",")
    parts = s.split(",")
    if len(parts) > 3:
        raise ValueError("an alias has at most two flag groups")
    body = parts[0]
    g1 = parts[1] if len(parts) > 1 else ""
    g2 = parts[2] if len(parts) > 2 else ""
    return normalize(body), _flag_group(g1, "flags"), _flag_group(g2, "private_flags")


# -------------------------------------------------------------------- matching

def _terms(q):
    return [t for t in q.split("-") if t]


def matches(query, alias):
    """Every normalized query term is a substring of the normalized, flag-stripped
    alias. Order-independent."""
    body, _, _ = parse_alias(alias)
    qbody, _, _ = parse_alias(query)
    ts = _terms(qbody)
    return bool(ts) and all(t in body for t in ts)


def search(query, aliases):
    """Return matching aliases in the normative order.

    Keys: most whole-segment matches, then earliest match, then highest coverage,
    then codepoint order. Applications holding their own signals (recency, frequency,
    favourites) may re-rank; this order is a default, not a prohibition.
    """
    qbody, _, _ = parse_alias(query)
    ts = _terms(qbody)
    scored = []
    for a in aliases:
        body, _, _ = parse_alias(a)
        if not ts or not all(t in body for t in ts):
            continue
        segs = body.split("-")
        whole = sum(1 for t in ts if t in segs)
        first = min(body.find(t) for t in ts)
        cover = sum(len(t) for t in ts) / len(body)
        scored.append((-whole, first, -cover, a))
    return [a for *_, a in sorted(scored)]
