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
from utina.acme import DEV, GAID, MARTA, NINA
from utina.cli.errors import ALIAS_PREFIX_AMBIGUOUS

__all__ = ["PARTIES", "SCOPE", "Aliases", "Party", "aliases_over"]

#: The scope every alias in this CLI shares. The whole world of these commands is one
#: governed domain, which is what makes COIA's empty-scope short form legitimate in a
#: column rather than an abbreviation of something longer (this.i @clscop).
SCOPE = "Acme"

#: The flag every alias here carries. COIA's 9 means an experimental, test or demo
#: environment with no real-world consequence to reputation, governance or cost, and
#: that is a literal description of Acme: the log is rebuilt from committed bytes on
#: every invocation and no decision on any screen binds anybody (this.i @clflg9).
FLAGS = coia.FLAG_TEST


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


#: Acme's cast, keyed by the alias constants ``utina.acme`` names them by. Marta and
#: Dev are the founders; Nina is the outside director the amendment seats at D4; the
#: domain itself is aliased too, so ``utina whois`` can answer for it.
PARTIES: Mapping[str, Party] = {
    GAID: Party("Acme", "governed domain"),
    MARTA: Party("Marta", "founder"),
    DEV: Party("Dev", "founder"),
    NINA: Party("Nina", "director"),
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
    _unflagged: Mapping[str, str]

    def full(self, identifier: str) -> str:
        """The scoped alias, for a line with room for it: ``9-marta-as-founder-at-acme``.

        An identifier this table does not know renders as *itself, in full*. Not
        truncated, because a truncated identifier is the thing this module exists to
        remove, and not relabelled, because inventing a name for an unrecognized party
        is a worse lie than showing the bytes.
        """
        return self._full.get(identifier, identifier)

    def short(self, identifier: str) -> str:
        """The unscoped alias, for a column: ``9-marta-as-founder``.

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
        whose alias is ``9-marta-as-founder-at-acme``. That is tolerance on the query
        only, in the same spirit as the spec's permissive hyphen regex, which likewise
        accepts on input a form it would not emit.

        Returns ``None`` rather than raising on a miss, so the caller decides whether
        an unmatched query is an error or merely an answer of no.
        """
        normalized = coia.normalize_query(query)
        if normalized in self._by_query:
            return self._by_query[normalized]
        if normalized in self._unflagged:
            return self._unflagged[normalized]
        if not query:
            return None
        matches = sorted(one for one in self._full if one.startswith(query))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ALIAS_PREFIX_AMBIGUOUS(prefix=query, matches=self.known())
        return None


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
    unflagged: dict[str, str] = {}
    for name, party in PARTIES.items():
        identifier = aids.get(name)
        if identifier is None:
            continue
        full[identifier] = coia.create_alias(party.who, party.role, SCOPE, FLAGS)
        short[identifier] = coia.create_alias(party.who, party.role, flags=FLAGS)
        by_query[full[identifier]] = identifier
        by_query[short[identifier]] = identifier
        # The same two aliases with no flag, for the query path only. Never displayed:
        # an unflagged alias is what COIA reserves for a verified, public, production
        # identifier, which is the one thing these must never appear to claim.
        unflagged[coia.create_alias(party.who, party.role, SCOPE)] = identifier
        unflagged[coia.create_alias(party.who, party.role)] = identifier
    return Aliases(
        scope=SCOPE, _full=full, _short=short, _by_query=by_query, _unflagged=unflagged
    )
