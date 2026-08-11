"""utina — a Custos evaluation engine.

Two planes, and no object performs both (Custos §1.3):

``utina.fold``
    Reads committed bytes, computes state, returns findings. Writes nothing and
    imports no KERI library.
``utina.enact``
    The constructor's verb. Produces committed events; every exercise of it is
    performed onto the record.
``utina.substrate``
    Everything KERI-facing, behind one interface, so the fold never sees it.
"""

__version__ = "0.0.0"
