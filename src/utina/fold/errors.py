"""What the codomain refuses to build, and the two codes that say why.

Two obstacles are possible inside a pure fold, and they are different in kind.

``GROUND_MISSING`` — ``e.state.ground-missing.f``
    A judgment was offered without the ground its value must carry. Custos makes
    that a typing failure rather than a validation nicety: "A finding is a
    judgment over a committed regime that carries its own ground — the citation,
    requirement, or proof that justifies it. A value that does not carry its
    ground is not a member of this type, whatever else it may be"
    (``custos-4.2.md:1504-1507``). So this is not "your finding is incomplete";
    it is "that is not a finding."

``MALFORMED_INPUT`` — ``e.input.malformed.f``
    A value handed to the fold is not the kind of thing it claims to be. Fail
    closed: an input the fold cannot check carries no authority, so it is
    refused at the door rather than coerced.

Both are classified by the **obstacle**, not by the component that noticed, which
is the Bakobo error-code rule and the reason one code serves many call sites
across four modules. A refusal is neither of these and never raises: Custos calls
it an operational fact recorded by the evaluator (``:1898-1900``), and you cannot
record what you threw — see ``utina.fold.refusal`` and this.i @zztcbs.

Derived in shape from bakobo/thesmo's ``m1-alpha`` reading (Apache-2.0, see
NOTICE); the codes and the messages are utina's, because thesmo predates the
Bakobo error-code standard and used exception classes.
"""

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

__all__ = ["GROUND_MISSING", "MALFORMED_INPUT", "require"]

GROUND_MISSING = ErrorCode(
    "e.state.ground-missing.f",
    "A judgment was constructed without the ground its value must carry.",
    detail=(
        "A judgment cannot be built without its ground: {value} was offered without "
        "{ground}, and a value that does not carry its ground is not a member of the "
        "finding codomain."
    ),
    args=("value", "ground"),
    hint=(
        "Build the value from the committed material that grounds it — the clause set, the "
        "citation, the typed requirement, or the proof package. Where the law supplies no "
        "such material, the answer is a refusal, which is not a finding at all."
    ),
)

MALFORMED_INPUT = ErrorCode(
    "e.input.malformed.f",
    "A value handed to the fold is not the kind of thing it claims to be.",
    detail=(
        "A value handed to the fold is not the kind of thing it claims to be: {field} must "
        "be {expected}, and {found} was given instead."
    ),
    args=("field", "expected", "found"),
    hint=(
        "The fold reads committed values and checks every one, because an input it cannot "
        "check carries no authority. Produce the value from committed bytes in the "
        "substrate and hand the checked result in."
    ),
)


def require(condition: bool, code: ErrorCode, **args: object) -> None:
    """Raise ``code`` with ``args`` unless ``condition`` holds.

    A named guard rather than a bare ``if``: every check in this package has one
    shape, so the shape is greppable and no branch quietly grows a second
    meaning.
    """
    if not condition:
        raise code(**args)
