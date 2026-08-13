#!/usr/bin/env python3
"""Cross-check ``src/utina/coia.py`` against the COIA spec's normative oracle.

The spec (https://github.com/dhh1128/coia) names its Python implementation the oracle,
and our module is a reimplementation: same convention, standard library only, because it
is expected to move to a repo of its own and a dependency would travel with it. The
difference in machinery is exactly where a faithful reimplementation goes wrong. The
oracle tests Unicode's ``Dash``, ``Quotation_Mark`` and ``White_Space`` binary
properties with the third-party ``regex`` engine; we enumerate their members and test
general categories with ``unicodedata``. This script is how we find out whether those
two things agree, over the spec's examples, the demo's aliases, a corpus of adversarial
Unicode, and optionally every code point in Unicode.

**It is not in CI, and it must not be.** It reads the oracle from a path outside this
repository — no checkout of utina contains it — and the oracle imports ``regex``, which
this repo deliberately does not depend on and will not add. The dependency is dodged by
running the oracle in a throwaway environment (``uv run --with regex --no-project``), so
nothing about this repo's manifest changes; but a CI job that depended on a directory in
a developer's home would be a lie about what CI checks. Run it by hand when either the
module or the spec changes.

Usage::

    tools/coia-oracle-check.py [--spec-dir DIR] [--no-sweep] [--stride N]

``--spec-dir`` defaults to ``$COIA_SPEC_DIR`` and then to ``~/code/me/coia``.

One class of divergence is expected and reported separately rather than failing the run:
the oracle's ``regex`` build and our ``unicodedata`` may carry different Unicode
versions, so a code point assigned in one and unassigned (``Cn``) in the other is
deleted by one side and kept by the other. Everything else is a real disagreement.

Two deliberate divergences from the oracle are also worth knowing about, because they
are choices rather than bugs. We reject flags that are not ASCII digits, where the
oracle's ``str.isdigit`` accepts Arabic-Indic and other digits that the spec's "single
ASCII digit" does not describe; and our scope template carries its own leading
separator, where the oracle prepends an extra space that normalization then collapses to
nothing. Neither is exercised below, since neither changes any alias the spec defines.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unicodedata
from typing import Any

REPO = pathlib.Path(__file__).resolve().parent.parent
MODULE = REPO / "src" / "utina" / "coia.py"
DEFAULT_SPEC_DIR = pathlib.Path.home() / "code" / "me" / "coia"

#: The oracle's own localization tables, for the four languages where its templates and
#: ours are the same sentence. Ours ships English; the other three are constructed here
#: exactly as ``tests/test_coia.py`` constructs them, so this checks the extension point
#: as well as the English path.
LOCALIZATIONS: dict[str, tuple[str, str, str]] = {
    "en": ("{flags}{who} as {role}{scope}", " at {org}", "me"),
    "pt": ("{flags}{who} como {role}{scope}", " na {org}", "eu"),
    "de": ("{flags}{who} als {role}{scope}", " bei {org}", "ich"),
    "es": ("{flags}{who} como {role}{scope}", " en {org}", "yo"),
    # Arabic as escapes, so the right-to-left script does not reorder this file on
    # screen: "{flags}{who} bisifati {role}{scope}", "fi {org}", and the pronoun "ana".
    "ar": (
        "{flags}{who} \u0628\u0635\u0641\u062a\u064a {role}{scope}",
        " \u0641\u064a {org}",
        "\u0623\u0646\u0627",
    ),
}

#: ``(lang, flags, who, role, scope)``, in the oracle's argument order. The spec's
#: Examples table, the demo's three actors, and then inputs chosen to break something:
#: mixed scripts, combining marks, control and format characters, fullwidth forms,
#: emoji, currency, an RTL name, and text that normalizes away to nothing.
ALIAS_CORPUS: list[tuple[str, str, str, str, str]] = [
    ("en", "", "", "CEO", "Acme"),
    ("en", "0", "Cecilia", "CEO", "Acme"),
    ("en", "90", "Bob", "Payee", "Bitcoin"),
    ("en", "09", "Bob", "Payee", "Bitcoin"),
    ("en", "", "Fred Perkins", "Business Exec", ""),
    ("en", "2", "Fred", "Cofounder", ""),
    ("en", "", "Acme", "Manufacturer", "Supply Chain"),
    ("en", "", "Cecilia", "Second Violin", "Vienna Symphony"),
    ("en", "9", "Marta", "Founder", "Acme"),
    ("en", "9", "Dev", "Founder", "Acme"),
    ("en", "9", "Nina", "Director", "Acme"),
    ("en", "9", "Marta", "Founder", ""),
    ("en", "9", "Dev", "Founder", ""),
    ("en", "9", "Nina", "Director", ""),
    ("en", "0123456789", "Bob", "Everything", "Everywhere"),
    ("en", "", "O\u2019Brien & Sons", "V.P.", "Acme, Inc."),
    ("en", "", "  spaced  out  ", "  role  ", "  scope  "),
    ("en", "", "ẞß", "Straße", "München"),
    ("en", "", "café", "baristá", "café"),
    ("en", "", "\uff26\uff55\uff4c\uff57", "\uff37\uff49\uff44\uff54\uff48", "\uff21"),
    ("en", "", "emoji \U0001f600 name", "role \U0001f3e2", "scope \u2705"),
    ("en", "", "control\u0085char", "role\u200bwith\u200bzwsp", "scope\ttab"),
    ("en", "", "Алексей", "инженер", "Газпром"),
    ("en", "", "דוד", "מנהל", "בנק"),
    ("en", "", "中文", "供应商", "工信部"),
    ("en", "", "สมชาย", "นักบัญชี", ""),
    ("en", "", "$100", "\u2211 analyst", "\u00a5en"),
    ("en", "", "---", "role", "\u2014\u2014"),
    ("en", "", "\u0640\u0640\u0640", "role", "tatweel"),
    ("en", "", "half\u00bd", "\u2167th legion", "\u2160"),
    ("en", "", "a\u200db", "zw\u200cj", "joiner"),
    ("en", "", "\U0001d5d4\U0001d5d5", "\U0001d41a\U0001d41b", "math alphanumerics"),
    ("pt", "", "João Silva", "Diretor Financeiro", "Caixa Geral de Depósitos"),
    ("de", "", "", "Vertriebsleiter", "Münchener Rück"),
    ("es", "02", "Juan", "Gerente Financiero", "BBVA"),
    ("es", "", "", "Gerente", ""),
    ("ar", "", "", "\u0645\u062d\u0627\u0633\u0628", ""),
    ("ar", "0", "\u0639\u0644\u064a", "\u0634\u0631\u064a\u0643", "\u0628\u0646\u0643"),
]

#: Strings fed straight to normalization, where the alias templates would otherwise hide
#: what is being tested. The edges matter most: leading and trailing whitespace, runs of
#: separators, and input that survives as nothing at all.
NORMALIZE_CORPUS: list[str] = [
    "",
    " ",
    "   \t\n  ",
    "-",
    "\u2014\u2014\u2014",
    "  Hello,  World!  ",
    "O\u2019Brien & Sons, Inc.",
    "café",
    "café",
    "A\u200bB",
    "test\u0085next",
    "tab\tsep",
    "a\x1cb",
    "a\x1fb",
    "½ pint",
    "Ⅷ legion",
    "ʿAbd al-Rahman",
    "5 + 3 = 8",
    "$100 café",
    "emoji \U0001f600 test",
    "a\u2010b",
    "\u2212x",
    "a\u3000b",
    "\u0640arabic tatweel",
    "ﷺ",
    "\uff21\uff22\uff06\uff23",
    "\u201cquoted\u201d",
    "\u2018\u2019",
    "「日本語」",
    "中文-测试",
    "İstanbul",
    "Ǆǅǆ",
    "ﬁre",
    "é́́x",
    "\U0001f1fa\U0001f1f8 flag",
    "line\u2028break",
    "para\u2029break",
    "nb\u00a0space",
    "narrow\u202fspace",
    "ogham\u1680space",
    "\uffff\ufffe unassigned",
    "\U000e0001 tag",
    "private\ue000use",
]

DRIVER = '''
import json
import sys
import unicodedata

sys.path.insert(0, sys.argv[1])
import coia

payload = json.load(open(sys.argv[2], encoding="ascii"))
result = {
    "unicode_version": unicodedata.unidata_version,
    "aliases": [coia.create_alias(*row) for row in payload["aliases"]],
    "normalized": [coia.normalize_unicode(text) for text in payload["normalized"]],
}
json.dump(result, sys.stdout)
'''


def load_module() -> Any:
    """Our implementation, loaded by file path rather than by package import.

    ``import utina.coia`` would work, but loading the file directly is the honest test:
    the module claims to stand alone, and this proves it does without the package around
    it. It is also what a sibling repo will do with the file.
    """
    spec = importlib.util.spec_from_file_location("coia_under_test", MODULE)
    if spec is None or spec.loader is None:  # pragma: no cover - a broken checkout
        raise SystemExit(f"Could not load {MODULE}")
    module = importlib.util.module_from_spec(spec)
    # Registered before execution because ``@dataclass`` resolves the defining module
    # through ``sys.modules``, and a module that is not there yet fails to build a class.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sweep_inputs(stride: int) -> list[str]:
    """One string per code point, each with the code point between two ASCII letters.

    The letters matter: a code point alone at the edge of a string is stripped by
    sub-step 4 if it is whitespace, which would hide a disagreement about whether it is
    whitespace at all. Between letters, every decision the six sub-steps make shows up
    in the result.
    """
    return [f"a{chr(cp)}b" for cp in range(0, 0x110000, stride)]


def run_oracle(spec_dir: pathlib.Path, aliases: list[Any], normalized: list[str]) -> Any:
    """The oracle's answers, computed in a throwaway environment that has ``regex``."""
    with tempfile.TemporaryDirectory() as tmp:
        driver = pathlib.Path(tmp) / "driver.py"
        driver.write_text(DRIVER, encoding="utf-8")
        payload = pathlib.Path(tmp) / "payload.json"
        payload.write_text(
            json.dumps({"aliases": aliases, "normalized": normalized}, ensure_ascii=True),
            encoding="ascii",
        )
        completed = subprocess.run(
            [
                "uv",
                "run",
                # Pinned to this interpreter's own version, because ``str.lower`` is
                # part of what is being compared and its case mappings grow with each
                # Unicode release. An oracle run on an older Python would report dozens
                # of differences that are the two runtimes disagreeing, not us.
                "--python",
                f"{sys.version_info.major}.{sys.version_info.minor}",
                "--with",
                "regex",
                "--no-project",
                "python",
                str(driver),
                str(spec_dir),
                str(payload),
            ],
            capture_output=True,
            text=True,
            cwd=tmp,
            check=False,
        )
    if completed.returncode != 0:
        raise SystemExit(
            f"The oracle did not run (exit {completed.returncode}). Check that "
            f"{spec_dir}/coia.py exists and that uv is on PATH.\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def is_version_skew(text: str, ours: str, theirs: str) -> bool:
    """Whether a disagreement is explained by the two sides' Unicode versions.

    A code point that one side's tables call unassigned and the other's call a letter is
    deleted by the first and kept by the second. That is a difference in what year the
    two engines' data was published, not in what either one implements, so it is
    reported and not counted as a failure.
    """
    unassigned = [character for character in text if unicodedata.category(character) == "Cn"]
    return bool(unassigned) and len(ours) < len(theirs)


def report(
    label: str,
    cases: list[str],
    ours: list[str],
    theirs: list[str],
    limit: int,
    detect_skew: bool = False,
) -> tuple[int, int]:
    """Print every disagreement in one batch; return the real and the skewed counts."""
    real = 0
    skewed = 0
    for case, mine, yours in zip(cases, ours, theirs, strict=True):
        if mine == yours:
            continue
        if detect_skew and is_version_skew(case, mine, yours):
            skewed += 1
            continue
        real += 1
        if real <= limit:
            print(f"  {label}: {case!a}\n    ours:   {mine!a}\n    oracle: {yours!a}")
    if real > limit:
        print(f"  ... and {real - limit} more {label} disagreements")
    return real, skewed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--spec-dir",
        type=pathlib.Path,
        default=pathlib.Path(os.environ.get("COIA_SPEC_DIR", DEFAULT_SPEC_DIR)),
        help="Directory holding the spec's coia.py oracle.",
    )
    parser.add_argument(
        "--no-sweep",
        action="store_true",
        help="Skip the code-point sweep and check only the curated corpus.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Sweep every Nth code point rather than every one of them.",
    )
    parser.add_argument("--limit", type=int, default=25, help="How many divergences to print.")
    args = parser.parse_args()

    oracle_path = args.spec_dir / "coia.py"
    if not oracle_path.is_file():
        raise SystemExit(
            f"No oracle at {oracle_path}. Clone https://github.com/dhh1128/coia and "
            f"pass --spec-dir, or set COIA_SPEC_DIR."
        )

    module = load_module()
    localizations = {
        lang: module.Localization(
            main_template=main_template, scope_template=scope_template, pronoun=pronoun
        )
        for lang, (main_template, scope_template, pronoun) in LOCALIZATIONS.items()
    }

    normalize_cases = list(NORMALIZE_CORPUS)
    if not args.no_sweep:
        normalize_cases += sweep_inputs(args.stride)

    ours_aliases = [
        module.create_alias(who, role, scope, flags, localization=localizations[lang])
        for lang, flags, who, role, scope in ALIAS_CORPUS
    ]
    ours_normalized = [module.normalize(text) for text in normalize_cases]

    print(f"Oracle: {oracle_path}")
    print(f"Cases: {len(ALIAS_CORPUS)} aliases, {len(normalize_cases)} normalizations")
    answers = run_oracle(args.spec_dir, [list(row) for row in ALIAS_CORPUS], normalize_cases)
    theirs = answers["unicode_version"]
    print(f"Unicode: ours {unicodedata.unidata_version}, oracle-side {theirs}")

    alias_labels = [f"{lang} {row}" for lang, *row in ALIAS_CORPUS]
    alias_real, _ = report("alias", alias_labels, ours_aliases, answers["aliases"], args.limit)
    normalize_real, skewed = report(
        "normalize",
        normalize_cases,
        ours_normalized,
        answers["normalized"],
        args.limit,
        detect_skew=True,
    )

    if skewed:
        print(f"{skewed} normalization case(s) differ only by Unicode version; not counted.")
    total = alias_real + normalize_real
    if total:
        print(f"DIVERGENT: {total} disagreement(s) with the oracle.")
        return 1
    print("AGREED: every case matches the oracle.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
