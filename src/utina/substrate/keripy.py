"""The real substrate: keripy identifiers, keripy digests, a keripy key log.

This is the one module in utina permitted to import a KERI library, and
``tests/test_purity.py`` is what keeps that true. Everything above the seam gets
the same five answers it got from the facade; what changes is that an identifier
here is a prefix derived from a real inception event, a SAID is Blake3-256 over
KERI's own JSON, a signature is Ed25519, and an amendment's anchor is a seal in a
rotation that any KERI tool can read out of the database this leaves on disk.

Three things are worth knowing before changing anything here.

**One key order, imposed three times.** keripy's ``Saider.saidify`` digests a
mapping in *insertion* order; ``canonical.py`` sorts. Two conventions meeting
inside one substrate would compute the identifier over one byte image and the
signature over another, and the whole failure would surface as ``verify``
returning ``False`` — a digest bug wearing a signature bug's clothes. So exactly
one function, :meth:`KeripySubstrate._sad`, decides the order — identifier
first, everything else sorted, signature excluded — and ``said``, ``sign`` and
``verify`` all go through it. No method here serializes a body it did not build
(this.i @fy5lwj).

**Determinism is pinned, not hoped for.** A KERI key event carries no timestamp,
so a KEL is byte-reproducible once its key material is. The salt is a literal,
the inception order is the composition root's, and the stretch tier is fixed by
``store``: an ephemeral store stretches at the fast tier and a durable one at
Argon2's, which means the same salt yields *different* identifiers in the two
modes. That is stated rather than discovered (this.i @7jrbt3).

**A signature carries the key state it was made under.** Resolving a verifier's
keys from *current* key state would mean Acme's rotation at beat D4 silently
invalidated everything the gAID signed before it — an ENDORSED slot becoming
PENDING with no error anywhere. So the opaque string this returns is the
establishment event's SAID, a dot, and the indexed signature, and ``verify``
resolves that event's keys out of the key log rather than today's (@zk27gz).
"""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from pathlib import Path
from types import TracebackType
from typing import Any

from keri.app import habbing  # type: ignore[import-untyped]
from keri.core import eventing  # type: ignore[import-untyped]
from keri.core.coring import Saider, dumps  # type: ignore[import-untyped]
from keri.core.indexing import Siger  # type: ignore[import-untyped]
from keri.core.signing import Salter  # type: ignore[import-untyped]
from keri.core.structing import SealDigest  # type: ignore[import-untyped]

from .canonical import canonical_json
from .errors import AID_UNKNOWN, ALIAS_TAKEN, STORE_NOT_OURS
from .protocol import AID, SAID

#: The demo's pinned salt: sixteen literal bytes. Correct for a fixture whose
#: purpose is reproducible replay, and a key-management failure in production.
DEMO_SALT = b"utina-demo-salt!"

#: The name the keystore and the event database are filed under. One environment
#: holds every party, because they are one domain's parties.
STORE_NAME = "utina"

#: What a directory this substrate created has in it, so that clearing a durable
#: store for a fresh deterministic run can never clear a directory it did not make.
MARKER = ".utina-keri-store"

#: The identifier field, and the field a signature lives in. Neither is digested
#: as it stands: the first is dummied, the second removed.
SAID_FIELD = "d"
SIGNATURE_FIELD = "sig"

#: Separates the establishment event's SAID from the indexed signature. Not in
#: the qb64 alphabet, so it cannot occur inside either half.
COORDINATE = "."

#: The single-signature, single-next-key shape every party is incepted with.
_SINGLE_SIG = {"icount": 1, "isith": "1", "ncount": 1, "nsith": "1"}


class KeripySubstrate:
    """A substrate over a real ``Habery``. Implements ``Substrate``.

    Holds the keystore, the event database and the key manager for its whole
    life, so it is a context manager and the composition root owns the ``with``.
    """

    def __init__(self, *, store: Path | None = None, salt: bytes = DEMO_SALT) -> None:
        """``store`` is where the key log is kept, or ``None`` for an ephemeral one.

        A durable store is what lets an independent KERI tool read what this
        wrote; an ephemeral one is what tests want, and it is roughly thirty
        times faster, because the two stretch key material at different tiers.
        """
        self._store = store
        self._salt = Salter(raw=salt).qb64
        self._hby: Any = None

    # -- lifecycle ------------------------------------------------------------

    def __enter__(self) -> KeripySubstrate:
        self._hby = habbing.Habery(
            name=STORE_NAME,
            base="",
            temp=self._store is None,
            headDirPath=None if self._store is None else str(self._prepared_store()),
            salt=self._salt,
        )
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._hby.close(clear=self._store is None)

    def _prepared_store(self) -> Path:
        """An empty directory of our own making, so a rerun starts from nothing.

        A durable store that survived the last run would make the second run's
        inception fail on an alias already taken, and a substrate that quietly
        reused it would produce a record whose identifiers depend on how many
        times the demo has been given. Refuses to empty a directory it cannot
        show it created, because the alternative is a program that deletes a
        path somebody typed.
        """
        store = self._store
        assert store is not None  # only reached when a store was asked for
        if store.exists():
            if not (store / MARKER).exists():
                raise STORE_NOT_OURS(store=str(store), marker=MARKER)
            shutil.rmtree(store)
        store.mkdir(parents=True)
        (store / MARKER).write_text(
            "Written by utina --substrate keripy. Deleted and rebuilt on every run.\n",
            encoding="utf-8",
        )
        return store

    # -- identity -------------------------------------------------------------

    def incept(self, alias: str) -> AID:
        """A prefix that is a digest of the inception event this just wrote."""
        if self._hby.habByName(alias) is not None:
            raise ALIAS_TAKEN(alias=alias)
        prefix: str = self._hby.makeHab(name=alias, **_SINGLE_SIG).pre
        return prefix

    def rotate(self, aid: AID, anchor: SAID) -> SAID:
        """Seal ``anchor`` into a rotation, and return that rotation's identifier.

        A digest seal, which is what anchoring the digest of something that is
        not itself a KERI event means. The rotation is a real establishment
        event: new signing keys, the pre-committed next keys rolled forward, and
        the seal in ``a`` where any KERI tool looks for one.
        """
        hab = self._hab(aid)
        hab.rotate(data=[SealDigest(d=anchor)._asdict()])
        said: str = hab.kever.serder.said
        return said

    def anchoring_event(self, said: SAID) -> SAID | None:
        """The establishment event that sealed ``said``, read out of the key log.

        A walk rather than a remembered mapping. The binding this reports is
        then a fact about committed KERI bytes, which is the claim beat D4
        makes; a dictionary beside the key log would be a cache that can
        disagree with the log it describes.
        """
        for prefix in self._hby.habs:
            for serder in self._hby.db.getEvtPreIter(pre=prefix):
                for seal in serder.sad.get("a") or ():
                    if seal.get(SAID_FIELD) == said:
                        found: str = serder.said
                        return found
        return None

    # -- committed bytes ------------------------------------------------------

    def said(self, body: Mapping[str, object]) -> SAID:
        """Blake3-256 over KERI's JSON, with the identifier field dummied.

        ``Saider.saidify`` requires the label to be present before it will fill
        it in, and utina's callers hand in a body that has never had one, so the
        empty field is put there here.
        """
        saider, _ = Saider.saidify(sad=self._sad(body, said=""))
        return str(saider.qb64)

    def sign(self, aid: AID, body: Mapping[str, object]) -> str:
        """The establishment event that signed, and the indexed signature."""
        hab = self._hab(aid)
        siger = hab.sign(self._raw(body), indexed=True)[0]
        return f"{hab.kever.lastEst.d}{COORDINATE}{siger.qb64}"

    def verify(self, aid: AID, body: Mapping[str, object], signature: str) -> bool:
        """Total, and fail-closed, over a library that raises freely.

        keripy raises ``KeyError`` on an unknown prefix and ``ShortageError`` or
        ``UnexpectedCodeError`` on malformed CESR, where the protocol requires
        ``False``. Catching broadly is the contract rather than laziness: the
        set of ways a stranger's bytes can be wrong is not ours to enumerate,
        and every one of them means the same thing here — no authority.
        """
        try:
            established, _, qb64 = signature.partition(COORDINATE)
            if not qb64:
                return False
            serder = self._hby.db.evts.get(keys=(aid, established))
            if serder is None:
                return False
            verified, _ = eventing.verifySigs(
                raw=self._raw(body),
                sigers=[Siger(qb64=qb64)],
                verfers=serder.verfers,
            )
            return bool(verified)
        except Exception:
            return False

    # -- internals ------------------------------------------------------------

    def _hab(self, aid: AID) -> Any:
        hab = self._hby.habs.get(aid)
        if hab is None:
            raise AID_UNKNOWN(aid=aid)
        return hab

    @staticmethod
    def _sad(body: Mapping[str, object], *, said: str | None = None) -> dict[str, object]:
        """The one field order every digest and every signature here is taken over.

        Identifier first, because that is where KERI puts it and where
        ``saidify`` reads it; then every other field sorted, because a caller's
        insertion order may not reach committed bytes; and never the signature,
        because a signature is an attachment and signing may not move a SAID.
        """
        fields = canonical_json(body)
        assert isinstance(fields, dict)  # a body is a mapping, and stays one
        held = fields.get(SAID_FIELD, "") if said is None else said
        ordered: dict[str, object] = {SAID_FIELD: held}
        for key, value in fields.items():
            if key not in (SAID_FIELD, SIGNATURE_FIELD):
                ordered[key] = value
        return ordered

    def _raw(self, body: Mapping[str, object]) -> bytes:
        """The bytes a signature is made over: the sealed event, sans signature."""
        serialized: bytes = dumps(self._sad(body))
        return serialized
