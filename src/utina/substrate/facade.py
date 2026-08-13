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
from .errors import AID_UNKNOWN, ALIAS_TAKEN
from .protocol import AID, SAID

#: Domain separation for derived key material, so a key can never be mistaken
#: for a digest of anything else this module computes.
_KEY_DOMAIN = b"utina-facade-key\x00"

#: The signature's code, chosen to look like what it stands in for.
_SIG_CODE = "0B"


class FacadeSubstrate:
    """The demo's substrate. Implements :class:`~utina.substrate.Substrate`."""

    def __init__(self) -> None:
        self._key_index: dict[AID, int] = {}
        self._kel_seq: dict[AID, int] = {}
        self._anchors: dict[SAID, SAID] = {}

    def __enter__(self) -> FacadeSubstrate:
        """A lifecycle this backend does not need, and its sibling does.

        The facade holds three dictionaries and nothing to close. It is a context
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
        """The establishment event that sealed ``said``, if one did."""
        return self._anchors.get(said)

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

    def _require_known(self, aid: AID) -> None:
        if aid not in self._key_index:
            raise AID_UNKNOWN(aid=aid)

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
