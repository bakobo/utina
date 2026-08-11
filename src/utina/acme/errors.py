"""The fixture's error codes.

Both are the same obstacle in two shapes: the record does not hold what was
asked for. They exist rather than a bare ``KeyError`` because a test that
addresses the log by the wrong label should say which label, and against what.
"""

# bakobo-errors ships no py.typed marker yet, so mypy cannot see its annotations.
from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

LABEL_UNKNOWN = ErrorCode(
    code="e.state.label-unknown.f",
    title="Acme's log has no position by that label.",
    detail=(
        "The position {label} was asked for, and the labels this corpus commits are {known}. "
        "A label names a beat of docs/demo-script.md, so an unknown one is either a typo or a "
        "beat the corpus does not tell yet."
    ),
    args=("label", "known"),
    hint="The labels are inception, board-seated, and d1 through d9.",
)

NAME_UNKNOWN = ErrorCode(
    code="e.state.name-unknown.f",
    title="Acme's log has no event by that name.",
    detail=(
        "The event named {name} was asked for, and the names this corpus commits are {known}."
    ),
    args=("name", "known"),
    hint="Names are the act kinds Acme committed, plus inception and seat-the-board.",
)
