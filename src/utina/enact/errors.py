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

REGISTRY_UNOPENED = ErrorCode(
    code="e.state.registry-unopened.f",
    title="This domain has no credential registry yet.",
    detail=(
        "A seat credential for {organ} was asked for and the domain {gaid} has opened no "
        "registry, so the credential would be unrevokable. A standing-conferring credential "
        "that cannot be revoked leaves registry state unaskable, and registry state is the "
        "evidence a standing judgment is computed over."
    ),
    args=("gaid", "organ"),
    hint="Open the domain's registry before seating an organ under it.",
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

EDGE_UNVALIDATED = ErrorCode(
    code="e.proof.edge-unvalidated.f",
    title="The credential cited as this endorser's qualification does not bear them out.",
    detail=(
        "{aid} offered an endorsement citing {qualification} as the credential that qualifies "
        "them to give it, and edge validation refuses the citation: under the DI2I operator "
        "the citing credential's issuer must be the cited credential's issuee, or a delegated "
        "identifier of it. The endorsement was issued and anchored in the endorser's own key "
        "log — they really did make the claim — and it was not committed to the record, "
        "because an endorsement whose qualification does not validate confers nothing."
    ),
    args=("aid", "qualification"),
    hint=(
        "Cite the credential whose issuee is the endorser, or an identifier delegated from "
        "that issuee. An endorser who holds no such credential cites none."
    ),
)

CITATION_UNKNOWN = ErrorCode(
    code="e.state.citation-unknown.f",
    title="This record carries no credential by that identifier.",
    detail=(
        "{aid} cited {qualification} as their qualification, and no issuance committed to this "
        "record embeds a credential with that identifier. A citation a stranger cannot resolve "
        "from the record is not a qualification; it is a claim about something invisible."
    ),
    args=("aid", "qualification"),
    hint="Issue the credential into the domain's registry first, then cite its identifier.",
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
