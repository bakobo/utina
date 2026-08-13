"""COIA: human-friendly aliases for identifiers no human can remember.

An opaque identifier — an AID, a DID, a public key, a payment address — is unusable as
a label, so every wallet and key manager lets its user attach a comment and then offers
no guidance about what to write. The Conventions for Opaque Identifier Aliases (COIA
v1, https://github.com/dhh1128/coia) supply the guidance: answer three questions about
the subject — *who*, in what *role*, in what *scope* — expand them into a localized
template, prefix any flags that warn about the identifier's semantics, and normalize the
result into a single lowercase token joined by hyphens, so that
``9-marta-as-founder-at-acme`` survives a URL, a log file, a chat message and being read
aloud.

**An alias is creator-local and carries no security claim.** It delivers the
human-friendly corner of Zooko's triangle for the person who created it and for nobody
else. The spec is emphatic: for anyone else "an alias might be suggestive, but it is not
a commitment to meaning. An alias can evolve without warning to suit its creator's
fancy. It must be treated as a lookup convenience, not as an identifier in its own
right, and it must be considered unresolvable outside the creator's context. Parsing
someone else's aliases for strong meaning is a dangerous antipattern."

So nothing downstream may infer authority, verification, or identity from an alias.
``0-cecilia-as-ceo-at-acme`` records that its creator has *not* verified Cecilia; the
absence of that flag records only that the creator believed otherwise. The flags are a
reminder to a human, never an input to a decision — the evidence a decision rests on is
committed elsewhere, and an alias is a label stuck on the outside of it.

This module implements the convention with the standard library alone, because it is
expected to move to a repo of its own and a dependency would travel with it. That costs
something: the spec's matching regex uses ``\\p{L}`` and ``\\p{N}``, which Python's
``re`` cannot compile at all, and the normalization rules are written against Unicode's
``Dash``, ``Quotation_Mark`` and ``White_Space`` binary properties, which ``re`` cannot
test either. Both are therefore implemented against ``unicodedata.category`` and the
enumerated property tables below. ``tools/coia-oracle-check.py`` checks the result
against the spec's normative implementation, which does have a full regex engine.

It imports nothing from ``utina`` and must not begin to: ``who``, ``role`` and ``scope``
are arguments, supplied by whatever composition root knows them.
``tests/test_coia.py`` enforces that by AST inspection.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

__all__ = [
    "ALIAS_REGEX",
    "AMPERSANDS",
    "DASHES",
    "DISALLOWED_CATEGORIES",
    "ENGLISH",
    "FLAG_MEANINGS",
    "FLAG_PAIRWISE",
    "FLAG_TEST",
    "FLAG_UNVERIFIED",
    "HYPHEN",
    "HYPHEN_ALTERNATIVES",
    "LOCALIZATIONS",
    "MAX_FLAGS",
    "PERIODS_AND_COMMAS",
    "PERMISSIVE_ALIAS_REGEX",
    "PUNCTUATION_TO_SPACE",
    "QUOTATION_MARKS",
    "WHITE_SPACE",
    "Localization",
    "create_alias",
    "localization_for",
    "matches_alias",
    "normalize",
    "normalize_query",
]

# --------------------------------------------------------------------------------------
# The flag vocabulary (spec step 4).
# --------------------------------------------------------------------------------------

FLAG_UNVERIFIED = "0"
"""The subject has not been verified in a way that eliminates man-in-the-middle risk."""

FLAG_PAIRWISE = "2"
"""The identifier is for pairwise or private use and should not be shared."""

FLAG_TEST = "9"
"""The identifier belongs to a test, demo or experimental environment with no real-world
consequences, and must not be used where production side effects are intended."""

FLAG_MEANINGS: dict[str, str] = {
    FLAG_UNVERIFIED: (
        "The subject of this identifier has not been verified, so any theory about who "
        "is behind it is suspect."
    ),
    FLAG_PAIRWISE: (
        "This identifier is intended for pairwise or private contexts only and should "
        "not be shared."
    ),
    FLAG_TEST: (
        "This identifier belongs to a test or demo environment and has no real-world "
        "consequences."
    ),
}
"""What each flag digit warns its reader about, in the words a UI can show.

The mapping is deliberately not exhaustive of what a caller may pass: the spec defines
these three and leaves the rest of the digits open, so an unknown digit is carried into
the alias rather than rejected. A flag nobody recognizes is still a signal that
something about this identifier is unusual."""

MAX_FLAGS = 10
"""No alias needs more warnings than there are digits, and a longer string is a caller
that has mistaken the flags argument for something else."""

# --------------------------------------------------------------------------------------
# Unicode property tables.
#
# Python's ``re`` has no ``\p{...}`` syntax and ``unicodedata`` exposes categories but
# not binary properties, so the three binary properties the spec relies on are
# enumerated here as their full membership. Each set is the complete list of code points
# carrying that property; they change only when Unicode adds a character, which is why
# they are written as escapes with the character named in the comment rather than as
# literals that a text editor could mangle.
# --------------------------------------------------------------------------------------

HYPHEN = "-"
"""The one separator a canonical alias contains: U+002D HYPHEN-MINUS."""

HYPHEN_ALTERNATIVES = frozenset(
    "\u2010"  # HYPHEN
    "\u2011"  # NON-BREAKING HYPHEN
    "\u2012"  # FIGURE DASH
    "\u2013"  # EN DASH
    "\u2212"  # MINUS SIGN
)
"""What a user's keyboard or word processor may have produced instead of a hyphen.

These are the five the spec's permissive matching pattern tolerates. They are not
tolerated in a *canonical* alias — normalization never emits one — but a query typed on
a locale keyboard or pasted out of a document may well contain them."""

DASHES = frozenset(
    # 002D hyphen-minus, 058A Armenian, 05BE Hebrew maqaf, 1400 Canadian, 1806 Mongolian
    "\u002d\u058a\u05be\u1400\u1806"
    # 2010-2015 the hyphen and dash block, 2053 swung dash
    "\u2010\u2011\u2012\u2013\u2014\u2015\u2053"
    # 207B superscript minus, 208B subscript minus, 2212 minus sign
    "\u207b\u208b\u2212"
    # 2E17-2E5D supplemental punctuation, 301C wave dash, 3030 wavy dash, 30A0 katakana
    "\u2e17\u2e1a\u2e3a\u2e3b\u2e40\u2e5d\u301c\u3030\u30a0"
    # FE31-FF0D presentation and fullwidth forms
    "\ufe31\ufe32\ufe58\ufe63\uff0d"
    # 10D6E Garay, 10EAD Yezidi
    "\U00010d6e\U00010ead"
)
"""Every member of Unicode's ``Dash`` binary property.

Wider than the ``Pd`` general category on purpose, because that is what the property
says: it takes in U+2212 MINUS SIGN and the superscript and subscript minus signs, which
are mathematical symbols, and U+301C WAVE DASH. All of them read as a hyphen to a human,
so all of them become a word break."""

QUOTATION_MARKS = frozenset(
    # 0022 quotation mark, 0027 apostrophe, 00AB and 00BB guillemets
    "\u0022\u0027\u00ab\u00bb"
    # 2018-201F the curly single and double quotes, 2039 and 203A single guillemets
    "\u2018\u2019\u201a\u201b\u201c\u201d\u201e\u201f\u2039\u203a"
    # 2E42 double low-reversed, 300C-301F CJK corner and white corner brackets
    "\u2e42\u300c\u300d\u300e\u300f\u301d\u301e\u301f"
    # FE41-FF63 presentation, fullwidth and halfwidth forms
    "\ufe41\ufe42\ufe43\ufe44\uff02\uff07\uff62\uff63"
)
"""Every member of Unicode's ``Quotation_Mark`` binary property.

This is what turns ``O'Brien`` into ``o-brien``: the apostrophe is a quotation mark, and
the spec maps quotes to spaces rather than deleting them, so the name does not
silently become ``obrien``."""

AMPERSANDS = frozenset(
    "\u0026"  # AMPERSAND
    "\ufe60"  # SMALL AMPERSAND
    "\uff06"  # FULLWIDTH AMPERSAND
)
"""Ampersands, which stand for a word and so leave a word break behind them."""

PERIODS_AND_COMMAS = frozenset(
    "\u002e"  # FULL STOP
    "\u002c"  # COMMA
    "\u060c"  # ARABIC COMMA
    "\u201a"  # SINGLE LOW-9 QUOTATION MARK, used as a comma in several languages
    "\u2024"  # ONE DOT LEADER
    "\u3002"  # IDEOGRAPHIC FULL STOP
    "\ufe52"  # SMALL FULL STOP
    "\uff0e"  # FULLWIDTH FULL STOP
    "\uff61"  # HALFWIDTH IDEOGRAPHIC FULL STOP
)
"""Sentence punctuation that separates words rather than joining them.

These would otherwise be deleted along with the rest of ``\\p{P}`` in sub-step 5, which
would turn ``Acme, Inc.`` into ``acmeinc``."""

PUNCTUATION_TO_SPACE = DASHES | QUOTATION_MARKS | AMPERSANDS | PERIODS_AND_COMMAS
"""Sub-step 3: everything that becomes a space rather than disappearing.

The distinction is whether a reader hears a word boundary there. A dash, a quote, an
ampersand, a period and a comma all separate; the rest of Unicode's punctuation, handled
in sub-step 5, does not."""

WHITE_SPACE = frozenset(
    # 0009-000D tab, newline, vertical tab, form feed, carriage return; 0020 space
    "\u0009\u000a\u000b\u000c\u000d\u0020"
    # 0085 next line, 00A0 no-break space, 1680 Ogham space mark
    "\u0085\u00a0\u1680"
    # 2000-200A the en quad through hair space
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    # 2028 line separator, 2029 paragraph separator
    "\u2028\u2029"
    # 202F narrow no-break space, 205F medium mathematical space, 3000 ideographic space
    "\u202f\u205f\u3000"
)
"""Every member of Unicode's ``White_Space`` binary property.

Enumerated rather than delegated to ``str.isspace``, which is not the same set: Python
also calls the file, group, record and unit separators (U+001C to U+001F) whitespace,
and Unicode does not. That difference is load-bearing here. Those four are control
characters, so sub-step 5 deletes them, and a string that used one as a separator closes
up into a single word instead of gaining a hyphen — which is what the spec's ordering
says must happen, and what the oracle does."""

DISALLOWED_CATEGORIES = frozenset(
    {"Cc", "Cf", "Cs", "Co", "Cn", "So", "Sm", "Sc", "Sk", "Lm"}
)
"""Sub-step 5's general categories: characters that are lossy, ambiguous, or awkward.

Control and format characters, surrogates, private-use and unassigned code points, and
the symbol categories that cover emoji, dingbats, mathematical operators, currency and
modifier symbols. ``Lm`` joins them because a modifier letter such as U+02BF or the
Arabic tatweel carries no sound a reader could speak back."""

DISALLOWED_CATEGORY_PREFIXES = ("P", "M")
"""Whole category families sub-step 5 deletes: all punctuation not already turned into a
space, and all combining marks, which after NFKC are the ones left with nothing to
combine with."""

# --------------------------------------------------------------------------------------
# Matching (spec, "Comparing").
# --------------------------------------------------------------------------------------

ALIAS_REGEX = r"^[\p{L}\p{N}]+(-[\p{L}\p{N}]+)*$"
"""The spec's pattern for a canonical alias, verbatim.

Published as a string because that is all it can be here: ``re.compile`` rejects
``\\p{L}`` outright. Engines that implement Unicode property escapes — PCRE, Java, .NET,
JavaScript with the ``u`` flag, Python's third-party ``regex`` — take it as written.
``matches_alias`` is the working equivalent for callers who only have the standard
library."""

PERMISSIVE_ALIAS_REGEX = (
    r"^[\p{L}\p{N}]+([-\u2010\u2011\u2012\u2013\u2212][\p{L}\p{N}]+)*$"
)
"""The spec's more permissive pattern, which tolerates the hyphen a keyboard produced.

Use it on what a user typed, never on what was stored: normalization emits U+002D and
nothing else, so an alias matching this but not ``ALIAS_REGEX`` has not been
normalized."""


@dataclass(frozen=True)
class Localization:
    """One language's templates, which is everything the convention localizes.

    English is the only localization this module ships (``ENGLISH``), because a
    localization that no test exercises is a claim rather than a feature. Appendix A of
    the spec tabulates a dozen more, and a caller who needs one constructs it here and
    passes it in — the same object the English path uses, so a new language is data
    rather than a code change.
    """

    main_template: str
    """Expanded with ``flags``, ``who``, ``role`` and ``scope``; the English form is
    ``{flags}{who} as {role}{scope}``."""

    scope_template: str
    """Expanded with ``org``, and carrying its own leading separator, because not every
    language separates the scope phrase from the role with a space."""

    pronoun: str
    """The word for "me", which fills ``who`` in a reflexive alias — one whose subject
    is the person creating it."""


ENGLISH = Localization(
    main_template="{flags}{who} as {role}{scope}",
    scope_template=" at {org}",
    pronoun="me",
)
"""The English templates from Appendix A."""

LOCALIZATIONS: dict[str, Localization] = {"en": ENGLISH}
"""Localizations by language code. One entry, and adding another means adding tests for
it: the repo gates on branch coverage, and a template nobody has ever expanded is
exactly the kind of thing that is wrong in a way no one notices until a demo."""


def localization_for(lang: str) -> Localization:
    """The registered localization for ``lang``, or a refusal naming the language.

    Falling back to English would be worse than failing: an alias in the wrong language
    reads as though its creator chose it, and the creator is the only person it is for.
    """
    if lang not in LOCALIZATIONS:
        raise ValueError(
            f"No COIA localization is registered for {lang!r}. Register one in "
            f"LOCALIZATIONS, or construct a Localization and pass it to create_alias."
        )
    return LOCALIZATIONS[lang]


def normalize(text: str) -> str:
    """Step 7's six sub-steps, in the order the spec gives them.

    The order is not incidental, and two pairs of sub-steps show why. Punctuation
    becomes a space (3) before disallowed characters are deleted (5), so a comma leaves
    a word break behind and an exclamation mark does not. Deletion (5) happens before
    whitespace is collapsed (6), so a control character that Python happens to consider
    whitespace — a tab, a NEL — disappears rather than becoming a hyphen.

    The result is a token of letters and digits joined by U+002D, or the empty string if
    nothing survived; ``matches_alias`` is the predicate for the difference.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = "".join(
        " " if character in PUNCTUATION_TO_SPACE else character for character in text
    )
    text = _strip_whitespace_edges(text)
    text = "".join(character for character in text if not _is_disallowed(character))
    return _collapse_whitespace_to_hyphen(text)


def normalize_query(query: str) -> str:
    """What a user typed, in the form it must be compared in.

    The spec's "Comparing" rule: a user looking up an alias is remembering a person and
    a role, not a token, so they will type capitals, spaces and punctuation. Normalizing
    the query makes ``9 Marta as Founder at Acme`` and ``9-MARTA-AS-FOUNDER-AT-ACME``
    both find ``9-marta-as-founder-at-acme``.

    It is a distinct name rather than a comment on ``normalize`` so that a lookup path
    which forgot the rule reads as obviously wrong.
    """
    return normalize(query)


def matches_alias(text: str, *, permissive: bool = False) -> bool:
    """Whether ``text`` is shaped like an alias: ``ALIAS_REGEX`` as a predicate.

    ``permissive`` switches to ``PERMISSIVE_ALIAS_REGEX``, which also accepts the five
    hyphen alternatives in ``HYPHEN_ALTERNATIVES``. Use it on a query, not on stored
    data: normalization emits U+002D and nothing else, so a stored alias that needs the
    permissive form did not come from ``create_alias``.

    Neither pattern is compiled, because ``re`` cannot compile either one. The two
    Unicode properties are tested with ``unicodedata.category`` instead, which is
    exactly what ``\\p{L}`` and ``\\p{N}`` mean.
    """
    separators = {HYPHEN} | HYPHEN_ALTERNATIVES if permissive else {HYPHEN}
    segments = _split(text, separators)
    return all(_is_letters_and_numbers(segment) for segment in segments)


def create_alias(
    who: str,
    role: str,
    scope: str = "",
    flags: str = "",
    *,
    localization: Localization = ENGLISH,
    suffix: int | None = None,
) -> str:
    """An alias for the identifier that refers to ``who``, acting as ``role``.

    The seven creation steps of the spec, in one call: choose the template
    (``localization``), answer the three questions (``who``, ``role``, ``scope``),
    convert the scope to a phrase, order the flags, expand, optionally disambiguate with
    ``suffix``, and normalize.

    ``who`` may be empty, which is the reflexive case — the alias names the person
    creating it — and takes the localized pronoun. ``scope`` may be empty, which is the
    spec's concise default for a context not worth constraining, and leaves the scope
    phrase out entirely rather than leaving an empty one behind.

    ``suffix`` is step 6, and it is the caller's business rather than this module's: an
    alias need not be unique, and only the caller can see the other aliases it might
    collide with. Passing ``1`` yields ``bob-as-ceo-at-beta-corp-1``.

    The three preconditions raise plain ``ValueError`` rather than carrying a Bakobo
    error code, which the repo's error standard would otherwise require. They are not
    reachable by anything a user does: ``who``, ``role`` and ``scope`` are free text and
    are never rejected, so the only way to trip one is for a composition root to pass
    the wrong argument. That is a programming error, and a programming error wants a
    traceback rather than a code a caller might try to handle.
    """
    who = who.strip()
    role = role.strip()
    scope = scope.strip()
    flags = flags.strip()

    if not role:
        raise ValueError(
            "The role cannot be empty. It is what distinguishes this facet of the "
            "subject from every other one, and an alias without it discriminates "
            "nothing."
        )
    if not all(character in "0123456789" for character in flags):
        raise ValueError(
            f"Flags must be ASCII digits or empty, and {flags!r} is neither. Each flag "
            f"is one digit: 0 unverified, 2 pairwise, 9 test or demo."
        )
    if len(flags) > MAX_FLAGS:
        raise ValueError(
            f"Flags must be at most {MAX_FLAGS} characters, and {flags!r} is longer. "
            f"There are only ten digits, so a longer string is not a set of flags."
        )
    if suffix is not None and suffix < 0:
        raise ValueError(
            f"A disambiguating suffix cannot be negative, and {suffix} is. It counts "
            f"aliases that expanded the same way, in the manner of a browser numbering "
            f"repeated downloads."
        )

    if not who:
        who = localization.pronoun
    prefix = "".join(sorted(flags)) + " " if flags else ""
    phrase = localization.scope_template.format(org=scope) if scope else ""

    expanded = localization.main_template.format(
        flags=prefix, who=who, role=role, scope=phrase
    )
    if suffix is not None:
        expanded = f"{expanded} {suffix}"
    return normalize(expanded)


def _is_disallowed(character: str) -> bool:
    """Whether sub-step 5 deletes ``character``, by its Unicode general category."""
    category = unicodedata.category(character)
    return category in DISALLOWED_CATEGORIES or category[0] in DISALLOWED_CATEGORY_PREFIXES


def _strip_whitespace_edges(text: str) -> str:
    """Sub-step 4, over Unicode's ``White_Space`` rather than Python's idea of it."""
    start = 0
    while start < len(text) and text[start] in WHITE_SPACE:
        start += 1
    end = len(text)
    while end > start and text[end - 1] in WHITE_SPACE:
        end -= 1
    return text[start:end]


def _collapse_whitespace_to_hyphen(text: str) -> str:
    """Sub-step 6: every run of whitespace, however long, becomes one U+002D."""
    out: list[str] = []
    in_whitespace = False
    for character in text:
        if character in WHITE_SPACE:
            if not in_whitespace:
                out.append(HYPHEN)
            in_whitespace = True
        else:
            out.append(character)
            in_whitespace = False
    return "".join(out)


def _split(text: str, separators: set[str]) -> list[str]:
    """``text`` cut at every separator, keeping the empty pieces.

    The empty pieces are the point: they are how a leading, trailing or doubled
    separator fails the pattern, which is what ``+`` between the separators means.
    """
    segments = [""]
    for character in text:
        if character in separators:
            segments.append("")
        else:
            segments[-1] += character
    return segments


def _is_letters_and_numbers(segment: str) -> bool:
    """``[\\p{L}\\p{N}]+``: at least one character, all of them letters or digits."""
    if not segment:
        return False
    return all(unicodedata.category(character)[0] in ("L", "N") for character in segment)
