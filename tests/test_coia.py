"""COIA v1, checked against the spec's own published examples.

Every expectation in this file is a literal constant rather than a computation, and
that is the point: ``src/utina/coia.py`` is expected to move to a repo of its own, and
a test that recomputed the answer with the same code under test would travel as
decoration. The English rows and the four non-English rows are copied from the Examples
table of the COIA spec (https://github.com/dhh1128/coia, README.md "Examples"); the
inputs that produce them were derived by running the spec's normative oracle,
``coia.py`` in that repo, and each one is reproduced byte for byte here.

Six published rows are deliberately absent, because reproducing them would have meant
fudging the expectation rather than testing anything:

* both Chinese rows use U+4F5C U+4E3A and U+5411, which appear neither in the spec's
  own Appendix A (U+8EAB U+4E3A and U+5728) nor in the oracle's tables;
* the Japanese row keeps ``UFJ`` in capitals, which step 7's lowercasing removes;
* the Korean and Hebrew rows put the role and the scope in an order their own
  Appendix A templates do not produce;
* the Russian row is half transliterated (``kak glavnyj buhgalter``) and half
  Cyrillic, so no single language's template yields it.

The oracle depends on the third-party ``regex`` package, which this repo does not and
will not carry, so it is not imported here. ``tools/coia-oracle-check.py`` runs the
comparison against it out-of-band in a throwaway environment.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

from utina.coia import (
    ALIAS_REGEX,
    ENGLISH,
    FLAG_MEANINGS,
    FLAG_PAIRWISE,
    FLAG_TEST,
    FLAG_UNVERIFIED,
    HYPHEN_ALTERNATIVES,
    LOCALIZATIONS,
    PERMISSIVE_ALIAS_REGEX,
    Localization,
    create_alias,
    localization_for,
    matches_alias,
    normalize,
    normalize_query,
)

MODULE = pathlib.Path(__file__).resolve().parent.parent / "src" / "utina" / "coia.py"

#: The Examples table of the spec, as ``(flags, who, role, scope, alias)``. An empty
#: ``who`` is the reflexive case, where the alias names its own creator.
SPEC_EXAMPLES: tuple[tuple[str, str, str, str, str], ...] = (
    ("", "", "CEO", "Acme", "me-as-ceo-at-acme"),
    ("0", "Cecilia", "CEO", "Acme", "0-cecilia-as-ceo-at-acme"),
    ("90", "Bob", "Payee", "Bitcoin", "09-bob-as-payee-at-bitcoin"),
    ("", "Fred Perkins", "Business Exec", "", "fred-perkins-as-business-exec"),
    ("2", "Fred", "Cofounder", "", "2-fred-as-cofounder"),
    ("", "Acme", "Manufacturer", "Supply Chain", "acme-as-manufacturer-at-supply-chain"),
    (
        "",
        "Cecilia",
        "Second Violin",
        "Vienna Symphony",
        "cecilia-as-second-violin-at-vienna-symphony",
    ),
)

#: Two localizations from Appendix A, defined here rather than shipped in the module.
#: English is the only path the module carries; these exercise the extension point and,
#: more usefully, put non-ASCII letters through normalization, which must preserve
#: ``ã``, ``ó`` and ``ü`` while deleting the orphaned combining marks around them.
PORTUGUESE = Localization(
    main_template="{flags}{who} como {role}{scope}",
    scope_template=" na {org}",
    pronoun="eu",
)
GERMAN = Localization(
    main_template="{flags}{who} als {role}{scope}",
    scope_template=" bei {org}",
    pronoun="ich",
)
SPANISH = Localization(
    main_template="{flags}{who} como {role}{scope}",
    scope_template=" en {org}",
    pronoun="yo",
)
#: Arabic, written as escapes rather than as letters: the script is right-to-left, and a
#: literal would reorder the surrounding Python on screen. The template reads
#: "{flags}{who} bisifati {role}{scope}", the scope phrase "fi {org}", the pronoun "ana".
ARABIC = Localization(
    main_template="{flags}{who} \u0628\u0635\u0641\u062a\u064a {role}{scope}",
    scope_template=" \u0641\u064a {org}",
    pronoun="\u0623\u0646\u0627",
)

#: The non-English rows of the Examples table that are faithfully reproducible.
LOCALIZED_EXAMPLES: tuple[tuple[Localization, str, str, str, str, str], ...] = (
    (
        PORTUGUESE,
        "",
        "João Silva",
        "Diretor Financeiro",
        "Caixa Geral de Depósitos",
        "joão-silva-como-diretor-financeiro-na-caixa-geral-de-depósitos",
    ),
    (
        GERMAN,
        "",
        "",
        "Vertriebsleiter",
        "Münchener Rück",
        "ich-als-vertriebsleiter-bei-münchener-rück",
    ),
    (
        SPANISH,
        "02",
        "Juan",
        "Gerente Financiero",
        "BBVA",
        "02-juan-como-gerente-financiero-en-bbva",
    ),
    (
        # "me as accountant", reflexive and unscoped, in a right-to-left script.
        ARABIC,
        "",
        "",
        "\u0645\u062d\u0627\u0633\u0628",
        "",
        "\u0623\u0646\u0627-\u0628\u0635\u0641\u062a\u064a-\u0645\u062d\u0627\u0633\u0628",
    ),
)

#: The three aliases the Acme demo shows on screen, scoped and unscoped. All three
#: carry the ``9`` flag, because nothing the demo does has real-world consequences and
#: the alias is where a viewer should be able to see that.
ACME_ALIASES: tuple[tuple[str, str, str, str], ...] = (
    ("Marta", "Founder", "Acme", "9-marta-as-founder-at-acme"),
    ("Dev", "Founder", "Acme", "9-dev-as-founder-at-acme"),
    ("Nina", "Director", "Acme", "9-nina-as-director-at-acme"),
    ("Marta", "Founder", "", "9-marta-as-founder"),
    ("Dev", "Founder", "", "9-dev-as-founder"),
    ("Nina", "Director", "", "9-nina-as-director"),
)

#: Normalization, one sub-step at a time. Invisible characters are written as escapes,
#: so that a reader can see what a case is about and no editor can silently eat one.
#: Several cases pin the *order* of step 7's six sub-steps rather than any one of them:
#: a tab and a NEL disappear instead of becoming hyphens, because both are control
#: characters and step 5 deletes those before step 6 collapses whitespace.
NORMALIZATION_CASES: tuple[tuple[str, str], ...] = (
    ("  Hello,  World!  ", "hello-world"),
    ("O\u2019Brien & Sons, Inc.", "o-brien-sons-inc"),
    ("cafe\u0301", "café"),
    ("café", "café"),
    ("A\u200bB", "ab"),
    ("test\u0085next", "testnext"),
    ("tab\tsep", "tabsep"),
    ("a\x1cb", "ab"),
    ("½ pint", "12-pint"),
    ("Ⅷ legion", "viii-legion"),
    ("ʿAbd al-Rahman", "abd-al-rahman"),
    ("5 + 3 = 8", "5-3-8"),
    ("$100 café", "100-café"),
    ("emoji \U0001f600 test", "emoji-test"),
    ("a\u2010b", "a-b"),
    ("\u2212x", "x"),
    ("a\u2014\u2014b", "a-b"),
    ("a--b", "a-b"),
    ("no.dots.here", "no-dots-here"),
    ("\u201cquoted\u201d", "quoted"),
    ("\uff21\uff22\uff06\uff23", "ab-c"),
    ("\u0640arabic tatweel", "arabic-tatweel"),
    ("a\u3000b", "a-b"),
    ("Ünïcödé", "ünïcödé"),
    ("é\u0301x", "éx"),
    ("中文-测试", "中文-测试"),
    ("-", ""),
    ("   ", ""),
    ("", ""),
)


@pytest.mark.parametrize(("flags", "who", "role", "scope", "alias"), SPEC_EXAMPLES)
def test_a_published_english_example_is_reproduced_exactly(
    flags: str, who: str, role: str, scope: str, alias: str
) -> None:
    assert create_alias(who, role, scope, flags) == alias


@pytest.mark.parametrize(
    ("localization", "flags", "who", "role", "scope", "alias"), LOCALIZED_EXAMPLES
)
def test_a_published_non_english_example_is_reproduced_exactly(
    localization: Localization, flags: str, who: str, role: str, scope: str, alias: str
) -> None:
    assert create_alias(who, role, scope, flags, localization=localization) == alias


@pytest.mark.parametrize(("who", "role", "scope", "alias"), ACME_ALIASES)
def test_a_demo_alias_is_what_the_screen_will_show(
    who: str, role: str, scope: str, alias: str
) -> None:
    assert create_alias(who, role, scope, FLAG_TEST) == alias
    assert matches_alias(alias)


def test_the_flag_digits_are_sorted_numerically_whatever_order_they_arrive_in() -> None:
    """Flags are a set of warnings, so two callers who chose the same ones agree."""
    assert create_alias("Bob", "Payee", "Bitcoin", "90") == "09-bob-as-payee-at-bitcoin"
    assert create_alias("Bob", "Payee", "Bitcoin", "09") == "09-bob-as-payee-at-bitcoin"
    both = FLAG_UNVERIFIED + FLAG_PAIRWISE
    assert create_alias("Bob", "Payee", "", both) == "02-bob-as-payee"


def test_the_flag_vocabulary_is_the_three_the_spec_defines() -> None:
    assert (FLAG_UNVERIFIED, FLAG_PAIRWISE, FLAG_TEST) == ("0", "2", "9")
    assert set(FLAG_MEANINGS) == {"0", "2", "9"}
    assert "verified" in FLAG_MEANINGS[FLAG_UNVERIFIED]


def test_an_uninteresting_scope_is_simply_left_out() -> None:
    """The empty string is the spec's concise default for "no constrained context"."""
    assert create_alias("Beta Corp", "Domain Owner") == "beta-corp-as-domain-owner"
    assert create_alias("Beta Corp", "Domain Owner", "   ") == "beta-corp-as-domain-owner"


def test_an_empty_who_is_the_reflexive_case_and_takes_the_localized_pronoun() -> None:
    assert create_alias("", "CEO", "Acme") == "me-as-ceo-at-acme"
    assert create_alias("   ", "CEO", "Acme") == "me-as-ceo-at-acme"
    assert create_alias("", "Vertriebsleiter", localization=GERMAN) == "ich-als-vertriebsleiter"


def test_a_numeric_suffix_disambiguates_two_aliases_that_expand_the_same_way() -> None:
    """Step 6, which is optional and is the caller's choice rather than the module's."""
    assert create_alias("Bob", "CEO", "Beta Corp") == "bob-as-ceo-at-beta-corp"
    assert create_alias("Bob", "CEO", "Beta Corp", suffix=1) == "bob-as-ceo-at-beta-corp-1"
    assert create_alias("Bob", "CEO", "Beta Corp", suffix=0) == "bob-as-ceo-at-beta-corp-0"
    assert create_alias("Bob", "CEO", "Beta Corp", suffix=12) == "bob-as-ceo-at-beta-corp-12"


def test_an_alias_is_created_already_normalized() -> None:
    """Punctuation a user typed into a name never reaches the alias intact."""
    assert create_alias("O\u2019Brien & Sons", "V.P.", "Acme, Inc.") == (
        "o-brien-sons-as-v-p-at-acme-inc"
    )
    assert matches_alias(create_alias("O\u2019Brien & Sons", "V.P.", "Acme, Inc."))


@pytest.mark.parametrize(("raw", "expected"), NORMALIZATION_CASES)
def test_normalization_matches_the_spec_sub_step_by_sub_step(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


def test_a_typed_query_is_normalized_before_it_is_compared() -> None:
    """The spec's "Comparing" rule: capitals, spaces and punctuation in a query are
    not a mismatch, because the user typing them is remembering a name, not an alias."""
    alias = create_alias("Marta", "Founder", "Acme", FLAG_TEST)
    assert normalize_query("9 Marta as Founder at Acme") == alias
    assert normalize_query("  9-MARTA-AS-FOUNDER-AT-ACME  ") == alias
    assert normalize_query("Marta") != alias


def test_the_matching_regexes_are_published_verbatim() -> None:
    """The constants are the spec's own text, which Python's ``re`` cannot compile.

    That is not a defect in the spec — ``\\p{...}`` is standard in most engines — but it
    is the whole reason this module tests the two Unicode categories with
    ``unicodedata`` instead of compiling the pattern.
    """
    assert ALIAS_REGEX == r"^[\p{L}\p{N}]+(-[\p{L}\p{N}]+)*$"
    assert PERMISSIVE_ALIAS_REGEX == (
        r"^[\p{L}\p{N}]+([-\u2010\u2011\u2012\u2013\u2212]"
        r"[\p{L}\p{N}]+)*$"
    )
    with pytest.raises(re.error):
        re.compile(ALIAS_REGEX)


@pytest.mark.parametrize(
    "text",
    [
        "me-as-ceo-at-acme",
        "09-bob-as-payee-at-bitcoin",
        "café",
        "中文-测试",
        "joão-silva-como-diretor-financeiro-na-caixa-geral-de-depósitos",
        "a",
        "9",
    ],
)
def test_a_canonical_alias_matches_the_strict_pattern(text: str) -> None:
    assert matches_alias(text)
    assert matches_alias(text, permissive=True)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "-",
        "-leading",
        "trailing-",
        "double--hyphen",
        "has space",
        "has_underscore",
        "has.dot",
        "a\u2010b",
    ],
)
def test_a_non_canonical_string_fails_the_strict_pattern(text: str) -> None:
    assert not matches_alias(text)


def test_the_published_pattern_says_nothing_about_case() -> None:
    """``[\\p{L}\\p{N}]`` takes capitals, so matching is a weaker claim than canonical.

    This is the spec's pattern faithfully, not a gap in the predicate: a caller who
    needs to know that a string is what ``create_alias`` would have produced compares it
    with its own normalization, which is a stronger question than shape.
    """
    assert matches_alias("Marta-As-Founder")
    assert normalize("Marta-As-Founder") != "Marta-As-Founder"
    assert normalize("marta-as-founder") == "marta-as-founder"


@pytest.mark.parametrize(
    "hyphen", ["\u2010", "\u2011", "\u2012", "\u2013", "\u2212"]
)
def test_the_permissive_pattern_tolerates_the_hyphen_a_keyboard_produced(hyphen: str) -> None:
    """A user typing a query on a locale keyboard may not have an ASCII hyphen."""
    assert matches_alias(f"marta{hyphen}as{hyphen}founder", permissive=True)
    assert not matches_alias(f"marta{hyphen}as{hyphen}founder")
    assert hyphen in HYPHEN_ALTERNATIVES


@pytest.mark.parametrize(
    "text", ["", "\u2010", "a\u2010\u2010b", "a\u2010 b", "\u2014"]
)
def test_the_permissive_pattern_is_no_looser_than_that(text: str) -> None:
    assert not matches_alias(text, permissive=True)


def test_english_is_the_shipped_localization_and_the_registry_names_it() -> None:
    assert LOCALIZATIONS["en"] is ENGLISH
    assert localization_for("en") is ENGLISH
    assert ENGLISH.main_template == "{flags}{who} as {role}{scope}"
    assert ENGLISH.scope_template == " at {org}"
    assert ENGLISH.pronoun == "me"


def test_an_unknown_language_is_rejected_by_name() -> None:
    with pytest.raises(ValueError, match="No COIA localization is registered for 'kl'"):
        localization_for("kl")


def test_an_empty_role_is_rejected() -> None:
    """Without a role there is nothing to distinguish this facet from another, which
    is the whole discriminating power of the convention."""
    with pytest.raises(ValueError, match="The role cannot be empty"):
        create_alias("Marta", "")
    with pytest.raises(ValueError, match="The role cannot be empty"):
        create_alias("Marta", "   ")


def test_non_digit_flags_are_rejected() -> None:
    with pytest.raises(ValueError, match="Flags must be ASCII digits or empty"):
        create_alias("Marta", "Founder", "Acme", "9x")
    with pytest.raises(ValueError, match="Flags must be ASCII digits or empty"):
        create_alias("Marta", "Founder", "Acme", "unverified")


def test_more_than_ten_flags_are_rejected() -> None:
    with pytest.raises(ValueError, match="Flags must be at most 10 characters"):
        create_alias("Marta", "Founder", "Acme", "01234567890")
    assert create_alias("Marta", "Founder", "", "0123456789").startswith("0123456789-")


def test_a_negative_suffix_is_rejected() -> None:
    with pytest.raises(ValueError, match="A disambiguating suffix cannot be negative"):
        create_alias("Marta", "Founder", "Acme", suffix=-1)


def test_flags_are_trimmed_before_they_are_checked() -> None:
    """Every input is trimmed first, as the oracle does, so a stray space from a form
    field is not a programming error."""
    assert create_alias("  Marta  ", "  Founder  ", "  Acme  ", "  9  ") == (
        "9-marta-as-founder-at-acme"
    )


def imported_roots(tree: ast.AST) -> set[str]:
    """Top-level package name of every absolute import in a parsed module.

    ``import utina.fold`` and ``from utina.fold import x`` both yield ``utina``. A
    relative import yields nothing here, which is why the caller checks for those
    separately: inside ``src/utina`` a relative import reaches utina by definition.
    """
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.partition(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            roots.add(node.module.partition(".")[0])
    return roots


def relative_imports(tree: ast.AST) -> list[str]:
    """Every ``from . import x`` in a parsed module, rendered for an error message."""
    return [
        "." * node.level + (node.module or "")
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level > 0
    ]


def test_coia_imports_nothing_from_utina() -> None:
    """The module's transferability, enforced rather than intended.

    ``coia.py`` implements a public convention that has nothing to do with Custos, and
    it is expected to move to a repo of its own. It sits under ``src/utina`` for now
    only because that is where this demo's code lives, so the one thing that must not
    happen is for it to acquire a utina import in the meantime — including a lazy one
    inside a function body, which is why this reads the AST rather than the runtime
    import graph. Modelled on ``tests/test_purity.py``, which guards the KERI
    quarantine the same way.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"), filename=str(MODULE))
    offenders = {root for root in imported_roots(tree) if root == "utina"}
    assert not offenders, (
        "src/utina/coia.py imports utina. COIA is a standalone convention that is "
        "expected to move to a repo of its own, so it takes who, role and scope as "
        "arguments and reaches into nothing. Pass the value in from the composition "
        "root instead."
    )
    assert not relative_imports(tree), (
        f"src/utina/coia.py uses relative imports {relative_imports(tree)}, which "
        "reach into utina by definition."
    )


def test_the_guard_catches_a_utina_import_planted_in_coia() -> None:
    """The guard's own teeth, since a guard that cannot fail guards nothing."""
    planted = "def create_alias():\n    from utina.fold import slots\n    return slots\n"
    assert imported_roots(ast.parse(planted)) == {"utina"}
    assert imported_roots(ast.parse("import utina.cli.render\n")) == {"utina"}
    assert relative_imports(ast.parse("from . import fold\nfrom .fold import slots\n")) == [
        ".",
        ".fold",
    ]
    assert relative_imports(ast.parse("import unicodedata\n")) == []


def test_the_module_really_does_import_only_the_standard_library() -> None:
    """A vacuous purity test would pass forever after the module was gutted."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"), filename=str(MODULE))
    assert "unicodedata" in imported_roots(tree), "the Unicode work has gone missing"
    assert "regex" not in imported_roots(tree), "the third-party regex package is not a dep"
