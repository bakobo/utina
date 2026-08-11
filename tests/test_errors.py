"""What the codomain raises, and what its messages must be good enough to say.

Two codes carry every failure this commission can produce, and the contract
reserves them: ``e.state.ground-missing.f`` for a judgment offered without the
ground its value must carry, and ``e.input.malformed.f`` for a value that is not
the kind of thing it claims to be. Both are classified by the obstacle rather
than by the component that noticed, which is why one code serves a dozen call
sites in four modules.

The message tests are not decoration. Bakobo's error standard requires a
complete plain sentence that lets a reader tell this failure from a different
one, so "invalid input" is a defect and a test is the only thing that keeps it
out.
"""

import pytest
from bakobo.errors import BakoboError, ErrorCode, validate_code

from utina.fold.errors import GROUND_MISSING, MALFORMED_INPUT, require

CODES = [GROUND_MISSING, MALFORMED_INPUT]


@pytest.mark.parametrize("code", CODES, ids=lambda c: c.code)
def test_every_code_is_a_legal_bakobo_code(code: ErrorCode) -> None:
    """Legality is checked at import by the library; assert it here anyway."""
    validate_code(code.code)
    assert isinstance(code, ErrorCode)


def test_the_two_reserved_codes_are_the_ones_the_contract_reserves() -> None:
    """docs/interfaces.md reserves exactly these two spellings for the codomain."""
    assert GROUND_MISSING.code == "e.state.ground-missing.f"
    assert MALFORMED_INPUT.code == "e.input.malformed.f"


@pytest.mark.parametrize("code", CODES, ids=lambda c: c.code)
def test_every_failure_here_is_final_not_retryable(code: ErrorCode) -> None:
    """A ground does not arrive by waiting, and the same bytes malform forever."""
    assert code.code.endswith(".f")
    with pytest.raises(BakoboError) as raised:
        require(False, code, **{name: "x" for name in code.args})
    assert raised.value.retryable is False


def test_require_returns_quietly_when_the_condition_holds() -> None:
    assert require(True, GROUND_MISSING, value="a", ground="b") is None


def test_ground_missing_names_the_value_and_the_ground_it_lacks() -> None:
    with pytest.raises(BakoboError) as raised:
        require(
            False,
            GROUND_MISSING,
            value="an affirmed finding",
            ground="the clause set it was appraised under",
        )
    message = str(raised.value)
    assert "an affirmed finding" in message
    assert "the clause set it was appraised under" in message
    assert "e.state.ground-missing.f" in message


def test_malformed_input_names_the_field_what_was_expected_and_what_arrived() -> None:
    with pytest.raises(BakoboError) as raised:
        require(
            False,
            MALFORMED_INPUT,
            field="a position's sequence number",
            expected="a non-negative whole number",
            found="-1",
        )
    message = str(raised.value)
    assert "a position's sequence number" in message
    assert "a non-negative whole number" in message
    assert "-1" in message


@pytest.mark.parametrize("code", CODES, ids=lambda c: c.code)
def test_no_message_is_the_uninformative_kind_the_standard_forbids(code: ErrorCode) -> None:
    """A complete sentence that distinguishes this failure from a different one."""
    rendered = code.detail or code.title
    assert rendered.endswith(".")
    assert rendered[0].isupper()
    assert "invalid" not in rendered.lower()
    assert "something went wrong" not in rendered.lower()
    assert code.hint is not None


@pytest.mark.parametrize("code", CODES, ids=lambda c: c.code)
def test_every_placeholder_in_a_detail_is_a_declared_arg(code: ErrorCode) -> None:
    """A template naming an arg it does not declare fails only when it is raised."""
    assert code.detail is not None
    for name in code.args:
        assert "{" + name + "}" in code.detail
    assert code.detail.count("{") == len(code.args)
