"""Test fixtures.

The on-disk synthetic portfolio implements R-DRM-010 (offline fixture).
"""

from pathlib import Path

import pytest

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "portfolio_sample"


@pytest.fixture
def traces_dir() -> Path:
    return FIXTURE_ROOT / "traces"


@pytest.fixture
def spec_dir() -> Path:
    return FIXTURE_ROOT / "specs"


@pytest.fixture
def decision_dir() -> Path:
    return FIXTURE_ROOT / "decisions"
