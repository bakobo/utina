"""The obstacles only a command line has, and the codes that name them.

Everything else the CLI can fail on already has a code somewhere it belongs: an unknown
position label is ``utina.acme``'s ``e.state.label-unknown.f``, an unknown party is the
substrate's ``e.id.aid-unknown.f``, a disposition against nothing committed is
``utina.enact``'s ``e.state.subject-unknown.f``. Classification is by the obstacle rather
than by the component that noticed, so this module declares a code only where the
obstacle itself is new.

The two alias codes are here for the same reason: an alias exists only in the display
plane (this.i @cldspl), so a query that names no party is an obstacle no other plane
can even describe.

All of them are permanent. A command that will not parse will not parse on a second
attempt, a prefix that names two committed events will name the same two, and Acme's
parties are rebuilt identically on every invocation, so an alias that matches nothing
now will match nothing later.
"""

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

__all__ = [
    "ALIAS_PREFIX_AMBIGUOUS",
    "ALIAS_UNKNOWN",
    "COMMAND_MALFORMED",
    "SAID_PREFIX_AMBIGUOUS",
]

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

ALIAS_PREFIX_AMBIGUOUS = ErrorCode(
    code="e.input.multi.alias-prefix.f",
    title="That identifier prefix names more than one party.",
    detail=(
        "The prefix {prefix} is borne by several of this domain's identifiers: {matches}. "
        "Choosing one of them here would be deciding which party the caller meant, and "
        "the whole reason this command exists is that a prefix is not a safe way to tell "
        "two identifiers apart."
    ),
    args=("prefix", "matches"),
    hint="Give the alias instead, which is unambiguous: {matches}",
)

ALIAS_UNKNOWN = ErrorCode(
    code="e.input.unknown.alias.f",
    title="Nothing in this domain is called that.",
    detail=(
        "No party matches {query}, either as an alias or as an identifier prefix. An "
        "alias is creator-local, so it names something only inside the domain that "
        "created it. The parties this domain knows are: {known}."
    ),
    args=("query", "known"),
    hint="Run utina whois with one of the aliases above, or with an identifier prefix.",
)
