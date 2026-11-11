import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


@pytest.fixture(params=["command-envelope", "event-envelope"])
def contract(
    request: pytest.FixtureRequest,
) -> tuple[str, Draft202012Validator, dict[str, Any]]:
    name: str = request.param
    schema_file = CONTRACTS / "jsonschema" / f"{name}.v1.schema.json"
    example_file = CONTRACTS / "examples" / f"{name}.example.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    example = json.loads(example_file.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema, format_checker=FormatChecker(formats=["date-time"])
    )
    return name, validator, example


def test_synthetic_example(
    contract: tuple[str, Draft202012Validator, dict[str, Any]],
) -> None:
    name, validator, example = contract
    validator.validate(example)
    optional = "authorization_ref" if name == "command-envelope" else "account_id"
    validator.validate(
        {**example, optional: "synthetic-reference", "environment_id": "TRAINING"}
    )


def test_required_fields(
    contract: tuple[str, Draft202012Validator, dict[str, Any]],
) -> None:
    _, validator, example = contract
    for field in example:
        incomplete = example.copy()
        del incomplete[field]
        with pytest.raises(ValidationError) as error:
            validator.validate(incomplete)
        assert error.value.validator == "required"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("environment_id", "LIVE"),
        ("environment_id", "UNKNOWN"),
        ("schema_version", "2.0.0"),
        ("correlation_id", "  "),
        ("payload", []),
        ("unexpected_field", True),
    ],
)
def test_invalid_common_fields(
    contract: tuple[str, Draft202012Validator, dict[str, Any]],
    field: str,
    value: object,
) -> None:
    _, validator, example = contract
    with pytest.raises(ValidationError):
        validator.validate({**example, field: value})


@pytest.mark.parametrize(
    "value",
    [
        "2026-11-11T13:00:00",
        "2026-11-11T13:00:00-03:00",
        "2026-11-11T13:00:00-00:00",
        "2026-02-30T13:00:00Z",
        "invalidZ",
    ],
)
def test_timestamps_require_valid_utc(
    contract: tuple[str, Draft202012Validator, dict[str, Any]], value: str
) -> None:
    name, validator, example = contract
    fields = (
        ("issued_at", "expires_at")
        if name == "command-envelope"
        else (
            "event_time",
            "recorded_at",
        )
    )
    for field in fields:
        with pytest.raises(ValidationError) as error:
            validator.validate({**example, field: value})
        assert list(error.value.path) == [field]
        validator.validate({**example, field: "2026-11-11T13:00:00.120+00:00"})


def test_envelope_specific_constraints(
    contract: tuple[str, Draft202012Validator, dict[str, Any]],
) -> None:
    name, validator, example = contract
    invalid = (
        {"actor": {"type": "SERVICE"}, "authorization_ref": None}
        if name == "command-envelope"
        else {"aggregate_version": 0, "account_id": None}
    )
    for field, value in invalid.items():
        with pytest.raises(ValidationError):
            validator.validate({**example, field: value})
