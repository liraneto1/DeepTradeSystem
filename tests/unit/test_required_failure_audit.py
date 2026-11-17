"""Deliberate mandatory failure on an isolated audit branch only."""


def test_required_failure_blocks_pipeline() -> None:
    assert False, "Required failure audit: this test must block subsequent steps."
