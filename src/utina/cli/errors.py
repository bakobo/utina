"""The obstacles only a command line has, and the codes that name them.

Everything else the CLI can fail on already has a code somewhere it belongs: an unknown
position label is ``utina.domain``'s ``e.state.label-unknown.f``, an unknown party is the
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
    "BEAT_UNKNOWN",
    "COMMAND_MALFORMED",
    "SAID_PREFIX_AMBIGUOUS",
]

BEAT_UNKNOWN = ErrorCode(
    code="e.state.beat-unknown.f",
    title="This demo script has no beat by that name.",
    detail=(
        "The beat {beat} was asked for, and the beats this script has are {known}."
    ),
    args=("beat", "known"),
    hint=(
        "Run the whole script with no --beat to see them in order, or ask for one of "
        "the names above."
    ),
)
"""A beat is a RUN-OF-SHOW position and not a record label, which is why this exists
rather than reusing ``e.state.label-unknown.f``. The two namespaces are genuinely
different: demo 2's beats are numbered 1 to 26 and the record's labels are ``b5``,
``d1``, ``board-seated``. Reusing the label error told a reader that Acme's record
committed labels called ``1, 2, 3`` — a confident, specific and false answer, which is
the failure shape this repo refuses (found while widening that error for a second
domain, this.i @er57yvs7)."""

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

#: The parties are named by a *command* rather than listed here, and that is a
#: repair rather than a preference: the error machinery caps a detail's length,
#: so once the domain had five parties the enumeration came out cut mid-alias —
#: "9-marta-as…" — under a hint telling the reader to type one of them. A
#: fragment of an alias invites the same unsupportable comparison a fragment of
#: an identifier does (this.i @clcoia), and it is worse here, because a reader
#: who types it gets this same refusal back.
ALIAS_UNKNOWN = ErrorCode(
    code="e.input.unknown.alias.f",
    title="Nothing in this domain is called that.",
    detail=(
        "No party matches {query}, either as an alias or as an identifier prefix. An "
        "alias is creator-local, so it names something only inside the domain that "
        "created it. This domain knows {count} parties, and the law screen lists them "
        "with their aliases."
    ),
    args=("query", "count"),
    hint="Run utina law --at inception to see the parties, then whois one of them.",
)
