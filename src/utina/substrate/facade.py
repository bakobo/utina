"""A pure-Python substrate: deterministic by construction, and honest about it.

Every identifier and every signature this produces is a function of committed
bytes and a fixed seed, so two runs of the demo produce the same log down to
the byte and the replay beat means something. Nothing here is secret and
nothing here is a public-key signature: a facade signature is a keyed MAC over
an identifier's derived key state, unforgeable only to a party who does not
hold the seed. That is the right trade for a fixture whose purpose is
reproducible replay with no cryptographic dependency, and it is why the
``Substrate`` protocol exists — keripy replaces this whole file without the
fold noticing (this.i @h7l67i).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from collections.abc import Mapping
from types import TracebackType

from .canonical import SAID_PLACEHOLDER, canonical_bytes, digest
from .errors import ACDC_UNVERIFIABLE, AID_UNKNOWN, ALIAS_TAKEN, NOT_ISSUED, REGISTRY_UNKNOWN
from .protocol import (
    ACDC_DT,
    AID,
    DI2I,
    EDGE_NODE_FIELD,
    EDGE_OPERATOR_FIELD,
    EDGES_FIELD,
    ISSUED,
    REVOKED,
    SAID,
)

#: Domain separation for derived key material, so a key can never be mistaken
#: for a digest of anything else this module computes.
_KEY_DOMAIN = b"utina-facade-key\x00"

#: The signature's code, chosen to look like what it stands in for.
_SIG_CODE = "0B"

#: What a facade credential's version field holds. Deliberately not a sized
#: KERI version string: imitating the shape without the substance invites a
#: reader to trust it (this.i @d2nlhb), and the honest statement is that this
#: credential was produced by the facade.
ACDC_VERSION = "ACDCfacade"


def _edges(sad: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    """The edge nodes a credential carries, by name, ignoring the block's own fields.

    ``d`` is the edges block's own identifier and ``o`` a block-level operator;
    neither is an edge. Anything else whose value is not a mapping is not an edge
    node either, and a credential that carries no edges at all yields nothing —
    there is then nothing to validate and nothing being claimed.
    """
    block = sad.get(EDGES_FIELD)
    if not isinstance(block, Mapping):
        return {}
    return {
        name: node
        for name, node in block.items()
        if name not in ("d", EDGE_OPERATOR_FIELD) and isinstance(node, Mapping)
    }


def _issuee(sad: Mapping[str, object]) -> AID | None:
    """The identifier a credential is *about*: its attributes block's ``i``."""
    block = sad.get("a")
    if not isinstance(block, Mapping):
        return None
    issuee = block.get("i")
    return issuee if isinstance(issuee, str) else None


class FacadeSubstrate:
    """The demo's substrate. Implements :class:`~utina.substrate.Substrate`."""

    def __init__(self) -> None:
        self._key_index: dict[AID, int] = {}
        self._kel_seq: dict[AID, int] = {}
        self._anchors: dict[SAID, SAID] = {}
        self._delegators: dict[AID, AID] = {}
        self._registries: dict[SAID, AID] = {}
        self._states: dict[tuple[SAID, SAID], str] = {}
        self._credentials: dict[SAID, Mapping[str, object]] = {}

    def __enter__(self) -> FacadeSubstrate:
        """A lifecycle this backend does not need, and its sibling does.

        The facade holds a few dictionaries and nothing to close. It is a context
        manager anyway so that a composition root writes one ``with`` and does not
        have to know which backend is behind it.
        """
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    # -- identity -------------------------------------------------------------

    def incept(self, alias: str) -> AID:
        if alias in self._key_index:
            raise ALIAS_TAKEN(alias=alias)
        self._key_index[alias] = 0
        self._kel_seq[alias] = 0
        return alias

    def delegate(self, delegator: AID, alias: str) -> AID:
        """Both halves of a cooperative delegation, in the facade's own terms.

        The delegate is incepted like any party — its identifier is its alias
        here (this.i @crrtzf) — and then two things are recorded that the
        protocol's queries answer from: the delegator, and a seal of the
        delegated identifier in the delegator's own log, written through the
        same interaction an issuance uses. What keripy gets from a ``dip``
        naming ``di`` and an event seal, this gets from the pair.
        """
        self._require_known(delegator)
        delegated = self.incept(alias)
        self._delegators[delegated] = delegator
        self._interact(delegator, delegated)
        return delegated

    def delegator_of(self, aid: AID) -> AID | None:
        return self._delegators.get(aid)

    def rotate(self, aid: AID, anchor: SAID) -> SAID:
        self._require_known(aid)
        self._key_index[aid] += 1
        self._kel_seq[aid] += 1
        body: dict[str, object] = {
            "t": "rot",
            "i": aid,
            "s": self._kel_seq[aid],
            "k": (self._key_id(aid),),
            "a": ({"d": anchor},),
        }
        said = self.said(body)
        self._anchors[anchor] = said
        return said

    def anchoring_event(self, said: SAID) -> SAID | None:
        """The key event that sealed ``said``, if one did — rotation or interaction."""
        return self._anchors.get(said)

    # -- credentials ----------------------------------------------------------

    def open_registry(self, controller: AID, alias: str) -> SAID:
        """A registry identified by the digest of its own inception, as a TEL is.

        The facade's analogue of a ``vcp``: the identifier is a function of the
        controller and the alias, so it is the same on every run, and it is
        sealed into the controller's log through the same interaction an issuance
        uses. What keripy gets from a transaction-event log, this gets from two
        dictionaries — which is the whole facade in one sentence.
        """
        self._require_known(controller)
        registry = self.said({"t": "vcp", "ii": controller, "n": alias})
        self._registries[registry] = controller
        self._interact(controller, registry)
        return registry

    def revoke_acdc(self, registry: SAID, said: SAID) -> SAID:
        """A ``rev``: the registry's state moves, and the credential does not."""
        self._require_registry(registry)
        if self._states.get((registry, said)) != ISSUED:
            raise NOT_ISSUED(registry=registry, said=said)
        controller = self._registries[registry]
        revocation = self.said({"t": "rev", "i": said, "ri": registry, "dt": ACDC_DT})
        self._states[(registry, said)] = REVOKED
        self._interact(controller, revocation)
        return revocation

    def verify_edges(self, sad: Mapping[str, object]) -> bool:
        """DI2I over the delegations this substrate recorded.

        The facade's answer to what keripy's ``Verifier.verifyChain`` computes,
        and it implements the same semantics: the near credential's issuer must
        be the far node's issuee, *or* a delegated identifier of it at any
        depth. The first arm is DI2I being a superset of I2I; the second is one
        walk up the delegator chain, which terminates because a visited set
        bounds it even over a cycle this substrate could not actually record.
        """
        for node in _edges(sad).values():
            far = self._credentials.get(str(node.get(EDGE_NODE_FIELD)))
            if far is None or node.get(EDGE_OPERATOR_FIELD) != DI2I:
                return False
            if not self._holds(str(sad.get("i")), _issuee(far)):
                return False
        return True

    def _holds(self, issuer: AID, issuee: AID | None) -> bool:
        """Whether ``issuer`` is ``issuee``, or a delegate of it at any depth."""
        if issuee is None:
            return False
        seen: set[AID] = set()
        at: AID | None = issuer
        while at is not None and at not in seen:
            if at == issuee:
                return True
            seen.add(at)
            at = self._delegators.get(at)
        return False

    def registry_state(self, registry: SAID, said: SAID) -> str | None:
        """``None`` says the credential does not stand here, so an unknown
        registry is refused rather than answered: they mean different things."""
        self._require_registry(registry)
        return self._states.get((registry, said))

    def issue_acdc(
        self,
        issuer: AID,
        schema: SAID,
        attributes: Mapping[str, object],
        *,
        registry: SAID | None = None,
        edges: Mapping[str, object] | None = None,
    ) -> tuple[Mapping[str, object], str]:
        """A credential in the dossier schema's required shape, registry or not.

        The mirror of what the keripy backend produces with ``proving.credential``:
        same field set, same fixed ``dt``, its own digests. A registry adds the
        ``ri`` field the credential names its registry in, and an issuance the
        registry's state answers from. The anchor rides an interaction event —
        the key log advances, the key state does not — so a signature made
        before an issuance still verifies after it.
        """
        self._require_known(issuer)
        if registry is not None:
            self._require_registry(registry)
        block: dict[str, object] = {"dt": ACDC_DT, **attributes}
        block = {"d": self.said(block), **block}
        fields: dict[str, object] = {"v": ACDC_VERSION, "i": issuer, "s": schema, "a": block}
        if registry is not None:
            fields["ri"] = registry
        if edges is not None:
            edge_block: dict[str, object] = dict(edges)
            fields[EDGES_FIELD] = {"d": self.said(edge_block), **edge_block}
        sad: dict[str, object] = {"v": ACDC_VERSION, "d": self.said(fields), **fields}
        signature = self.sign(issuer, sad)
        if not self.verify(issuer, sad, signature):
            raise ACDC_UNVERIFIABLE(issuer=issuer)
        if registry is not None:
            self._states[(registry, str(sad["d"]))] = ISSUED
        self._credentials[str(sad["d"])] = sad
        self._interact(issuer, str(sad["d"]))
        return sad, signature

    # -- committed bytes ------------------------------------------------------

    def said(self, body: Mapping[str, object]) -> SAID:
        return digest(canonical_bytes(self._for_said(body)))

    def sign(self, aid: AID, body: Mapping[str, object]) -> str:
        self._require_known(aid)
        index = self._key_index[aid]
        return f"{_SIG_CODE}{index}.{self._mac(aid, index, body)}"

    def verify(self, aid: AID, body: Mapping[str, object], signature: str) -> bool:
        if aid not in self._key_index:
            return False
        prefix, separator, mac = signature.partition(".")
        if not separator:
            return False
        if not prefix.startswith(_SIG_CODE):
            return False
        index_text = prefix[len(_SIG_CODE) :]
        if not index_text.isdigit():
            return False
        index = int(index_text)
        if index > self._key_index[aid]:
            return False
        return hmac.compare_digest(mac, self._mac(aid, index, body))

    # -- internals ------------------------------------------------------------

    def _interact(self, aid: AID, anchor: SAID) -> SAID:
        """Seal ``anchor`` into an interaction event: the log moves, the keys stay."""
        self._kel_seq[aid] += 1
        body: dict[str, object] = {
            "t": "ixn",
            "i": aid,
            "s": self._kel_seq[aid],
            "a": ({"d": anchor},),
        }
        said = self.said(body)
        self._anchors[anchor] = said
        return said

    def _require_known(self, aid: AID) -> None:
        if aid not in self._key_index:
            raise AID_UNKNOWN(aid=aid)

    def _require_registry(self, registry: SAID) -> None:
        if registry not in self._registries:
            raise REGISTRY_UNKNOWN(registry=registry)

    @staticmethod
    def _for_said(body: Mapping[str, object]) -> dict[str, object]:
        """The bytes an identifier is computed over: placeholder in, signature out."""
        return {**{k: v for k, v in body.items() if k != "sig"}, "d": SAID_PLACEHOLDER}

    @staticmethod
    def _for_signature(body: Mapping[str, object]) -> dict[str, object]:
        """The bytes a signature is computed over: the sealed event, sans the signature."""
        return {k: v for k, v in body.items() if k != "sig"}

    @staticmethod
    def _key(aid: AID, index: int) -> bytes:
        seed = _KEY_DOMAIN + aid.encode("utf-8") + b"\x00" + str(index).encode("ascii")
        return hashlib.blake2b(seed, digest_size=32).digest()

    def _key_id(self, aid: AID) -> str:
        """The public name of an identifier's current key state."""
        return digest(self._key(aid, self._key_index[aid]))

    def _mac(self, aid: AID, index: int, body: Mapping[str, object]) -> str:
        raw = hmac.new(
            self._key(aid, index),
            canonical_bytes(self._for_signature(body)),
            hashlib.blake2b,
        ).digest()[:32]
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
