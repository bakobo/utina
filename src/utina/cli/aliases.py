"""What the screens call a party, and why that is never the party's identifier.

Every screen used to name a party by a twelve-character prefix of its identifier —
``acme:marta`` under the facade, ``EPFtMUsnh_BZ...`` under keripy. A prefix beside a
name invites a reader to decide that two identifiers are the same by comparing what
they can see, and it cannot support that decision: ``amp-diff.md`` section 4.3.8
treats a prefix as an entropy channel, faithful but unable to amplify a difference, so
an attacker matching twelve displayed characters grinds twelve characters. The rule
this module exists to hold is ``pill-design.md`` section 2.1: recognition is not
verification, and no equality decision may be made from a collapsed form. Full
identifiers are reachable, but only through the deliberate act of ``utina whois``
(this.i @clcoia, @clwhoi).

An alias is **display-only** (this.i @cldspl). COIA is explicit that it is a private
nickname: human-meaningful only for its creator, "not a commitment to meaning" for
anyone else, free to evolve without warning, and dangerous to parse for strong meaning.
So it must never enter committed bytes, never be an input to the fold, and never affect
a finding. That is why this module lives in ``utina.cli`` and not beside the record it
labels: ``utina.fold``, ``utina.enact`` and ``utina.acme`` cannot import it at all, and
``tests/test_purity.py`` fails if they ever do.

The table is keyed by the identifier inception returned, never by the alias constant
that asked for it, which is what makes both substrates render identically: the facade
returns its argument and keripy returns a digest of an inception event, and the screen
above is the same either way.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from utina import coia
from utina.acme import DEV, DEVICE, GAID, MARTA, QUINN, SEAT
from utina.cli.errors import ALIAS_PREFIX_AMBIGUOUS

__all__ = ["PARTIES", "SCOPE", "Aliases", "Party", "aliases_over"]

#: The scope every alias in this CLI shares. The whole world of these commands is one
#: governed domain, which is what makes COIA's empty-scope short form legitimate in a
#: column rather than an abbreviation of something longer (this.i @clscop).
SCOPE = "Acme"

#: The language every alias here is minted in. COIA requires a generator to reject a
#: language it does not support rather than falling back to another, so this is passed
#: rather than defaulted.
LANG = "en"

#: The flag every alias here carries. COIA 2.0's 6 is "throwaway, test, demo; no
#: real-world consequence", which is a literal description of Acme: the log is rebuilt
#: from committed bytes on every invocation and no decision on any screen binds
#: anybody (this.i @clflg9).
#:
#: **It used to be 9, and that was wrong after the 2.0 cutover.** Under COIA 1.x, 9
#: meant a test environment; under 2.0 it means "compromised — positive evidence that
#: the wrong party controls it". So every party on every screen was flagged as
#: captured by an attacker. CHANGES.md warns about this one inversion by name: flags
#: are lost across the version boundary but never inverted, except here.
FLAGS = "6"


@dataclass(frozen=True)
class Party:
    """The two answers COIA needs about a party, beyond the scope they share.

    ``who`` is enough of a name to be meaningful in the creator's context, and ``role``
    is the responsibility that distinguishes this facet of the subject from its others.
    Both are supplied here rather than derived from the identifier, because they are
    facts about Acme that no substrate knows.
    """

    who: str
    role: str

    #: The scope this party's alias carries, defaulting to the one they all share.
    #: The domain itself overrides it to empty: "acme governed domain at Acme" is
    #: circular, and COIA 4.1 says scope MAY be empty where the context is
    #: unconstrained — which is exactly the case for the identifier that IS the
    #: context.
    scope: str | None = None


#: Acme's cast, keyed by the alias constants ``utina.acme`` names them by.
#:
#: **The seat is Nina's, not Acme's**, and that is the substance rather than a naming
#: preference. ``custos-4.2.md:2145`` requires the seat credential to name "the organ's
#: AID as issuee"; the organ's AID is one Nina owns, dedicated to her capacity as that
#: seat, which is the role-dedicated-AID model of Provenant's own alias convention.
#: Under the previous reading the seat and its device were Acme's, so the record named
#: no accountable human anywhere and duplicity attached to an abstraction. Now it
#: attaches to her.
#:
#: **Quinn is Acme's CFO**, and being senior is the point of him. Beat 14 refuses his
#: endorsement of a budget act, and a refusal only teaches something when the refused
#: party had a plausible claim: a stranger being turned away surprises nobody, while a
#: chief financial officer who cannot approve the budget makes the room ask why. The
#: answer — that he prepares it and the board approves it — is the distinction the
#: beat exists to draw. Authority is not seniority.
#:
#: Nina has no separate personal AID here. She has many in life, and none of them is
#: any of this record's business; the only facet this narrative touches is the seat.
PARTIES: Mapping[str, Party] = {
    GAID: Party("Acme", "governed domain", scope=""),
    MARTA: Party("Marta", "founder"),
    DEV: Party("Dev", "founder"),
    SEAT: Party("Nina", "board seat 3"),
    DEVICE: Party("Nina", "board seat 3 device"),
    QUINN: Party("Quinn", "CFO"),
}


@dataclass(frozen=True)
class Aliases:
    """What each identifier is called, in both of the forms a screen may need.

    Both forms are precomputed at construction. The alternative is to call COIA on
    every render, which would put string normalization on the path of every line of
    every screen and would make the aliases a function of when they were asked for
    rather than of the record.
    """

    scope: str
    _full: Mapping[str, str]
    _short: Mapping[str, str]
    _by_query: Mapping[str, str]

    def full(self, identifier: str) -> str:
        """The scoped alias, for a line with room for it: ``marta-founder-acme,6``.

        An identifier this table does not know renders as *itself, in full*. Not
        truncated, because a truncated identifier is the thing this module exists to
        remove, and not relabelled, because inventing a name for an unrecognized party
        is a worse lie than showing the bytes.
        """
        return self._full.get(identifier, identifier)

    def short(self, identifier: str) -> str:
        """The unscoped alias, for a column: ``marta-founder,6``.

        Legitimate rather than abbreviated. Within these screens the scope is constant,
        so COIA's empty-scope form is an alias in its own right, and dropping a scope
        that every party shares removes no information a reader had (this.i @clscop).
        """
        return self._short.get(identifier, identifier)

    def every_alias(self) -> tuple[str, ...]:
        """Every scoped alias, sorted, for the header that discloses the cast."""
        return tuple(sorted(self._full.values()))

    def identifiers(self) -> tuple[str, ...]:
        """Every identifier this table can name, for substitution into fold prose."""
        return tuple(sorted(self._full))

    def known(self) -> str:
        """The aliases an error message should offer, as one readable clause.

        The unscoped forms, because an error is read on one line and four scoped
        aliases do not fit on one: within this domain the scope is constant anyway, and
        either form resolves.
        """
        return ", ".join(sorted(self._short.values()))

    def resolve(self, query: str) -> str | None:
        """The identifier ``query`` names, or ``None`` if it names nothing.

        Three ways in, in order of how confident each one is. An alias in either form
        matches after normalization, because COIA's Comparing section requires that a
        user who types capitals, spaces or punctuation be matched as if they had not.
        Failing that, the query is tried as an identifier prefix — @clhndl's surviving
        half, since a prefix remains a good thing to *type* even though it is no longer
        a good thing to print — and a prefix naming two parties is refused rather than
        guessed at, which is the same discipline the CLI already applies to an event
        identifier.

        The flags are part of the alias and are never dropped from what is *displayed*.
        On input they are optional, so ``Marta as Founder at Acme`` finds the party
        whose alias is ``marta-founder-acme,6``. That is tolerance on the query
        only, in the same spirit as the spec's permissive hyphen regex, which likewise
        accepts on input a form it would not emit.

        Returns ``None`` rather than raising on a miss, so the caller decides whether
        an unmatched query is an error or merely an answer of no.
        """
        # COIA 6.2: a reader MUST split flag groups off BEFORE normalizing the body,
        # because the reverse order destroys the comma that delimits them. Keying on
        # the normalized body alone is also what lets an unflagged query resolve while
        # an unflagged alias is never displayed — the flag is display, the body is
        # identity.
        try:
            body, _, _ = coia.parse_alias(query.strip())  # type: ignore[no-untyped-call]
        except ValueError:
            # A malformed flag group is a query that matches nothing, never an error:
            # this resolves what a person typed, and the caller decides whether a miss
            # is a refusal. ``parse_alias`` already normalizes the body it returns.
            return None
        normalized = body
        if normalized in self._by_query:
            return self._by_query[normalized]
        if not query:
            return None
        matches = sorted(one for one in self._full if one.startswith(query))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ALIAS_PREFIX_AMBIGUOUS(prefix=query, matches=self.known())
        return None


def _alias(who: str, role: str, scope: str = "", flags: str = "") -> str:
    """One COIA alias, and the only place the vendored implementation is called.

    The reference implementation is unannotated and stays that way — it is pinned
    byte-identical to upstream — so the typed/untyped boundary is crossed here once
    rather than at every call site.
    """
    minted: str = coia.create_alias(LANG, who, role, scope, flags)  # type: ignore[no-untyped-call]
    return minted


def aliases_over(aids: Mapping[str, str]) -> Aliases:
    """The alias table for the identifiers ``aids`` maps Acme's party names onto.

    The composition root's half of this commission. ``aids`` is what
    ``utina.acme.build`` got back from ``substrate.incept`` for each party, so the
    table is a function of the substrate's answers and the display facts in
    :data:`PARTIES`, and of nothing else. A party the table has no entry for is simply
    absent; :meth:`Aliases.full` then shows its identifier whole.
    """
    full: dict[str, str] = {}
    short: dict[str, str] = {}
    by_query: dict[str, str] = {}
    for name, party in PARTIES.items():
        identifier = aids.get(name)
        if identifier is None:
            continue
        scope = SCOPE if party.scope is None else party.scope
        full[identifier] = _alias(party.who, party.role, scope, FLAGS)
        short[identifier] = _alias(party.who, party.role, flags=FLAGS)
        # Keyed on the body with its flag group stripped, so a query resolves whether
        # or not it was typed with the flag. The flagged form is the only one ever
        # DISPLAYED: an unflagged alias is what COIA reserves for a verified public
        # identifier, which is the one thing these must never appear to claim.
        by_query[_alias(party.who, party.role, scope)] = identifier
        by_query[_alias(party.who, party.role)] = identifier
    return Aliases(
        scope=SCOPE, _full=full, _short=short, _by_query=by_query
    )
