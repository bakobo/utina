"""Why a record could not answer where it was pointed.

Four obstacles, and the first two are one obstacle in two shapes: the record does not
hold what was asked for. They exist rather than a bare ``KeyError`` because a caller
that addresses the log by the wrong label should be told which label, and against what.

The second two are the ones ``this.i`` @qtm5ntkg and @er57yvs7 added when a position
stopped being a label and started being a label *or* a sequence number. A domain that
commits no labels has nothing to offer as an alternative, so it says the true thing
instead — the labels are a demo's names for coordinates, and the record has sequence
numbers — and a sequence number the record does not reach is refused rather than folded
at, because a coordinate past the end answers a question about nothing.

A ``title`` and a ``hint`` do not vary with the occurrence; ``bakobo.errors`` fixes both
per code. That is why there are two label errors rather than one wording itself two
ways, and why no title here names a domain.
"""

# bakobo-errors ships no py.typed marker yet, so mypy cannot see its annotations.
from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

LABEL_UNKNOWN = ErrorCode(
    code="e.state.label-unknown.f",
    title="This domain's log has no position by that label.",
    detail=(
        "The position {label} was asked for in {domain}'s record, and its demo labels "
        "are {known}. A label names a beat of a demo script, so an unknown one is either a "
        "typo or a beat this record does not tell."
    ),
    args=("domain", "label", "known"),
    hint=(
        "A position is one of the labels the detail lists, or a sequence number. The list "
        "is truncated where it is long; a sequence number always works, because that is "
        "what the record itself commits."
    ),
)

LABELS_ABSENT = ErrorCode(
    code="e.state.labels-absent.f",
    title="This domain's record commits no position labels at all.",
    detail=(
        "The position {label} was asked for in {domain}'s record, which has no label table. "
        "A label is a demo's name for a coordinate and is committed nowhere. The record has "
        "sequence numbers, running from 0 to {last}, which is what a stranger folding the "
        "same log would address it by."
    ),
    args=("domain", "label", "last"),
    hint="Ask for a position by sequence number instead, as in --at 0 for the first event.",
)

POSITION_OUT_OF_RANGE = ErrorCode(
    code="e.input.range.position.f",
    title="That sequence number is past the end of the record.",
    detail=(
        "The position {seq} was asked for in {domain}'s record, whose committed events run "
        "from 0 to {last}. A coordinate the record does not reach would fold to an answer "
        "about nothing, which is a wrong answer delivered confidently, so it is refused."
    ),
    args=("domain", "seq", "last"),
    hint="Run utina log to see how far the record goes, and ask for a coordinate inside it.",
)

NAME_UNKNOWN = ErrorCode(
    code="e.state.name-unknown.f",
    title="This domain's log has no event by that name.",
    detail=(
        "The event named {name} was asked for in {domain}'s record, and the names it commits "
        "are {known}."
    ),
    args=("domain", "name", "known"),
    hint="Names are the act kinds this domain committed, plus inception.",
)
