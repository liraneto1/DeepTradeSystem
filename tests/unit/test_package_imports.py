from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "shared",
        "market_data",
        "features",
        "market_state",
        "ai",
        "control",
        "risk",
        "execution",
        "portfolio",
        "audit",
        "operations",
    ],
)
def test_domain_package_is_importable(module: str) -> None:
    qualified_name = f"trade_system.{module}"
    assert import_module(qualified_name).__name__ == qualified_name
