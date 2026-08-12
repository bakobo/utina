"""The two obstacles only a command line has, and the codes that name them.

Everything else the CLI can fail on already has a code somewhere it belongs: an unknown
position label is ``utina.acme``'s ``e.state.label-unknown.f``, an unknown party is the
substrate's ``e.id.aid-unknown.f``, a disposition against nothing committed is
``utina.enact``'s ``e.state.subject-unknown.f``. Classification is by the obstacle rather
than by the component that noticed, so this module declares a code only where the
obstacle itself is new.

Both are permanent. A command that will not parse will not parse on a second attempt,
and a prefix that names two committed events will name the same two.
"""

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

__all__ = ["COMMAND_MALFORMED", "SAID_PREFIX_AMBIGUOUS"]

COMMAND_MALFORMED = ErrorCode(
    code="e.input.malformed.command.f",
    title="That command line will not parse.",
    detail=(
        "The command could not be read: {detail}. Nothing was evaluated, and nothing was "
        "committed."
    ),
    args=("detail", "usage"),
    hint="Run utina --help, or {usage}",
)

SAID_PREFIX_AMBIGUOUS = ErrorCode(
    code="e.input.multi.said-prefix.f",
    title="That identifier prefix names more than one committed event.",
    detail=(
        "The prefix {prefix} is borne by several committed events: {matches}. An appraisal "
        "is a judgment over one subject's committed bytes, so choosing one of them here "
        "would be picking which act to judge on the caller's behalf."
    ),
    args=("prefix", "matches"),
    hint="Give more of the identifier, or the name the demo record commits the act under.",
)
