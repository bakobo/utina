"""A record utina did not write, rebuilt before it is folded (this.i @k6agmgtn).

Custos promises that "any stranger holding the logs computes the same
Constitution and the same findings" (``custos-4.2.md:31-34``). Until this module
the stranger was the one case utina could not be: the fold could consume only
what its own constructor wrote in the same process, and ``Corpus.load`` trusts
every identifier and signature it is handed.

A **record** is the gAID, the key logs of everyone who signs, founds or
delegates, and the GEL's events with their signatures, as plain JSON. It is
admitted only by rebuilding it in a substrate that wrote none of it:

1. every key log is replayed through the substrate's own verifier, so key state
   is computed from verified events rather than read;
2. every event's identifier is re-derived from its bytes;
3. every event's signature is verified, against the key state its signer's
   replayed log establishes;
4. and only then does ``fold/gel.py`` derive order and membership from the
   gAID's replayed log.

Anything the fold would not examine is refused rather than skipped
(this.i @gnviwwjc): a field the record does not define, an event of a kind no
fold module reads, a key log belonging to nobody who signs, founds or delegates.
A partial fold of a record is the proper subset ``custos-4.2.md:3178-3181`` names
as a must-reject.

What this does not verify, stated rather than discovered: the signature a
credential embedded in an event carries for its own issuer. The event's own
signature covers those bytes, and for an endorsement the event's signer is the
credential's issuer; for a certification it is the domain admitting a sponsor's
dossier, and the sponsor's own signature is not re-checked here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold.corpus import Corpus, Event
from utina.fold.gel import anchored
from utina.fold.triple import Position
from utina.substrate import AID, Substrate

#: What a record says it is, so a reader can refuse one it does not know.
FORMAT = "utina-record/1"

#: The fields a record carries, an entry in its key logs, and an event. A field
#: outside these is content nothing would examine.
RECORD_FIELDS = frozenset({"format", "gaid", "kels", "events"})
KEL_FIELDS = frozenset({"aid", "log"})
EVENT_FIELDS = frozenset({"said", "kind", "body"})

#: Every event kind some module of the fold reads, by the ilk its signed body
#: commits in ``t``. The kind label in a record sits outside every signature, so
#: it is checked against the body rather than believed: an endorsement relabelled
#: an act would otherwise stop counting toward unity. The constructor writes all
#: of these but ``retraction``, which the slot walk reads and nothing yet writes.
KINDS: Mapping[str, str] = {
    "icp": "inception",
    "enact": "enactment",
    "act": "act",
    "end": "endorsement",
    "ret": "retraction",
    "iss": "issuance",
    "rev": "revocation",
    "dup": "duplicity",
    "cert": "certification",
}

RECORD_MALFORMED = ErrorCode(
    code="e.input.record-malformed.f",
    title="This record carries something the fold would not examine.",
    detail=(
        "{problem} A record is folded whole or not at all: content the fold would "
        "skip is a part of the record nobody judged, and folding the rest would be "
        "folding a proper subset of what was presented."
    ),
    args=("problem",),
    hint="Present the record exactly as utina export wrote it.",
)

RECORD_UNVERIFIABLE = ErrorCode(
    code="e.proof.record-unverifiable.f",
    title="An event in this record does not verify.",
    detail=(
        "The event {said} {problem}. A record is admitted only by rebuilding it, "
        "and an event whose bytes or signature do not stand up is evidence of "
        "nothing."
    ),
    args=("said", "problem"),
    hint="Present the record exactly as its own engine wrote it, with every key log it needs.",
)


def export(events: Sequence[Event], gaid: AID, substrate: Substrate) -> dict[str, Any]:
    """The record of ``events``: what :func:`ingest` needs to rebuild them elsewhere.

    The key logs are those of the gAID, every signer, and every delegator of any
    of them, each delegator before its delegates so that a replay can accept a
    delegated inception. Nothing else is included, because :func:`ingest`
    refuses a key log nobody needs.
    """
    return {
        "format": FORMAT,
        "gaid": gaid,
        "kels": [
            {"aid": aid, "log": substrate.export_kel(aid)}
            for aid in _needed(events, gaid, substrate)
        ],
        "events": [
            {"said": event.said, "kind": event.kind, "body": dict(event.body)}
            for event in events
        ],
    }


def ingest(record: object, substrate: Substrate) -> Corpus:
    """Rebuild ``record`` in ``substrate`` and fold it, or refuse it whole.

    ``substrate`` must hold no key state of its own for any party in the record;
    it is the stranger. Every refusal is one of the two codes above, or one
    ``fold/gel.py`` or the substrate raises for the same reason. A substrate that
    refused a record may hold part of it and is not to be used again.
    """
    fields = _fields(record, RECORD_FIELDS, "The record")
    if fields["format"] != FORMAT:
        raise RECORD_MALFORMED(problem=f"The record is {fields['format']!r}, not {FORMAT}.")
    gaid = fields["gaid"]
    kels, entries = fields["kels"], fields["events"]
    if not isinstance(gaid, str) or not isinstance(kels, list) or not isinstance(entries, list):
        raise RECORD_MALFORMED(problem="The record's gaid, kels or events has the wrong shape.")
    replayed = [_replay(entry, substrate) for entry in kels]
    events = [_rebuilt(entry, substrate) for entry in entries]
    needed = set(_needed(events, gaid, substrate))
    unexamined = sorted(set(replayed) - needed)
    if unexamined:
        raise RECORD_MALFORMED(
            problem=f"The key logs of {', '.join(unexamined)} are needed by nothing here."
        )
    absent = sorted(needed - set(replayed))
    if absent:
        raise RECORD_MALFORMED(
            problem=(
                f"The record needs the key logs of {', '.join(absent)} and does not carry "
                "them; key state the stranger already held is not evidence this record "
                "presented."
            )
        )
    return anchored(events, substrate.key_events(gaid), gaid=gaid)


def _fields(value: object, allowed: frozenset[str], what: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != allowed:
        found = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        raise RECORD_MALFORMED(
            problem=f"{what} carries {found} where it carries exactly {sorted(allowed)}."
        )
    return value


def _replay(entry: object, substrate: Substrate) -> AID:
    fields = _fields(entry, KEL_FIELDS, "A key-log entry")
    aid, log = fields["aid"], fields["log"]
    if not isinstance(aid, str) or not isinstance(log, str):
        raise RECORD_MALFORMED(problem="A key-log entry's aid or log is not text.")
    substrate.ingest_kel(aid, log)
    return aid


def _rebuilt(entry: object, substrate: Substrate) -> Event:
    fields = _fields(entry, EVENT_FIELDS, "An event entry")
    said, kind, body = fields["said"], fields["kind"], fields["body"]
    if not isinstance(said, str) or not isinstance(body, Mapping):
        raise RECORD_MALFORMED(problem="An event entry's said or body has the wrong shape.")
    if kind not in KINDS.values():
        raise RECORD_MALFORMED(problem=f"The event {said} is a {kind!r}, which no fold reads.")
    if KINDS.get(str(body.get("t"))) != kind:
        raise RECORD_UNVERIFIABLE(
            said=said, problem=f"is labelled {kind!r} and its signed ilk is {body.get('t')!r}"
        )
    if body.get("d") != said or substrate.said(body) != said:
        raise RECORD_UNVERIFIABLE(
            said=said, problem="has an identifier its bytes do not derive"
        )
    signer, signature, sn = body.get("i"), body.get("sig"), body.get("s")
    if not isinstance(signer, str) or not isinstance(signature, str):
        raise RECORD_UNVERIFIABLE(said=said, problem="names no signer or carries no signature")
    if not isinstance(sn, int) or isinstance(sn, bool) or sn < 0:
        raise RECORD_UNVERIFIABLE(said=said, problem="carries no GEL sequence number")
    if not substrate.verify(signer, body, signature):
        raise RECORD_UNVERIFIABLE(
            said=said, problem=f"does not carry a signature {signer}'s key log verifies"
        )
    return Event(said=said, kind=str(kind), position=Position(sn), body=dict(body))


def _needed(events: Sequence[Event], gaid: AID, substrate: Substrate) -> list[AID]:
    """The gAID, every signer, and their delegators, delegators first."""
    wanted: list[AID] = []

    def want(aid: AID) -> None:
        if aid in wanted:
            return
        delegator = substrate.delegator_of(aid)
        if delegator is not None:
            want(delegator)
        wanted.append(aid)

    want(gaid)
    for event in events:
        want(str(event.body["i"]))
    return wanted
