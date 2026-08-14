"""The constructor's error codes, declared as module-scope literals.

Classified by the obstacle: ``e.input.`` is material a caller handed us that
does not have the required shape, ``e.state.`` is a record that does not admit
the act being asked for, ``e.proof.`` is a signature that will not stand up.
"""

# bakobo-errors ships no py.typed marker yet, so mypy cannot see its annotations.
from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

DOMAIN_INCEPTED = ErrorCode(
    code="e.state.domain-incepted.f",
    title="This domain has already been founded.",
    detail=(
        "The domain {gaid} was incepted at an earlier coordinate, and inception was asked for "
        "again. A second founding law would leave two answers to the question of what law was "
        "in force at the start."
    ),
    args=("gaid",),
    hint="Amend the founding law with an enactment; inception happens once.",
)

DOMAIN_UNINCEPTED = ErrorCode(
    code="e.state.domain-unincepted.f",
    title="This domain has not been founded yet.",
    detail=(
        "An act was committed for {gaid} before its inception, so there is no law in force to "
        "judge it under and no key state it could have been signed with."
    ),
    args=("gaid",),
    hint="Call incept_domain with the founding law before committing anything else.",
)

SUBJECT_UNKNOWN = ErrorCode(
    code="e.state.subject-unknown.f",
    title="Nothing committed carries that identifier.",
    detail=(
        "A disposition by {aid} named {subject} as its subject, and no event with that "
        "identifier has been committed, so the disposition would refer to nothing a stranger "
        "could resolve."
    ),
    args=("aid", "subject"),
    hint="Commit the act or the enactment first, then dispose of it by its returned SAID.",
)

RECORD_UNRESUMABLE = ErrorCode(
    code="e.input.format.resume-record.f",
    title="These events do not read as one continuable record.",
    detail=(
        "Resuming expected the committed events in coordinate order, positions running from "
        "zero without a gap, and found position {found} where {expected} was required. The "
        "constructor takes its next coordinate from the record's length, so continuing over "
        "a gapped or permuted record would commit every later event at a coordinate the "
        "committed bytes contradict."
    ),
    args=("expected", "found"),
    hint="Hand resume the record's events exactly as committed: complete, in coordinate order.",
)

SIGNATURE_UNVERIFIABLE = ErrorCode(
    code="e.proof.signature-unverifiable.f",
    title="A signature this constructor just produced does not verify.",
    detail=(
        "The substrate signed the {kind} event for {aid} and then failed to verify its own "
        "signature over the same bytes. The event was not committed, because evidence nobody "
        "can check confers no authority."
    ),
    args=("kind", "aid"),
    hint=(
        "The substrate's signing and verifying paths disagree about the bytes. Suspect the "
        "canonical encoding or the key state the signature names."
    ),
)
