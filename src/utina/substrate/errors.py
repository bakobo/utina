"""The substrate's error codes, declared as module-scope literals.

Classified by the obstacle rather than by the component, so a caller can
prefix-match a branch of meaning: ``e.input.`` is bytes that will not commit,
``e.id.`` is an identifier the substrate cannot act as or act on.
"""

# bakobo-errors ships no py.typed marker yet, so mypy cannot see its annotations.
# Silenced at the import rather than in pyproject.toml, which this commission does
# not own; a mypy override for `bakobo.*` there would be the better fix.
from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

NOT_CANONICAL = ErrorCode(
    code="e.input.not-canonical.f",
    title="A value cannot be committed to canonical bytes.",
    detail=(
        "A {kind} appeared at {path} in the body being committed, and there is no canonical "
        "encoding for it, so the bytes a stranger would have to replay cannot be produced."
    ),
    args=("kind", "path"),
    hint=(
        "Commit strings, integers, booleans, null, exact fractions.Fraction values, mappings "
        "with string keys, and sequences of those. A weight is a Fraction, never a float, "
        "because unity has to stay decidable."
    ),
)

ALIAS_TAKEN = ErrorCode(
    code="e.id.alias-taken.f",
    title="An identifier with this alias already exists.",
    detail=(
        "The alias {alias} was incepted before, and inception was asked for again. Returning "
        "the existing identifier would let two parties share one voice without anybody "
        "noticing."
    ),
    args=("alias",),
    hint="Incept each party once, and hold the identifier the first inception returned.",
)

SUBSTRATE_UNKNOWN = ErrorCode(
    code="e.feature.substrate-unknown.f",
    title="This build carries no substrate by that name.",
    detail=(
        "A substrate called {name} was asked for, and the ones this build carries are "
        "{known}. Guessing at which was meant would silently decide what kind of "
        "identifier the whole record is written under."
    ),
    args=("name", "known"),
    hint="Pass one of the listed names. The facade is the default and needs no flag.",
)

AID_UNKNOWN = ErrorCode(
    code="e.id.aid-unknown.f",
    title="This substrate holds no key state for that identifier.",
    detail=(
        "An act was requested as {aid}, and this substrate has never incepted it, so there is "
        "no key state to act under and nothing it produced could be verified."
    ),
    args=("aid",),
    hint="Incept the identifier before signing or rotating as it.",
)
