"""Sample unit tests — replace with real tests."""

import package_name
from package_name.settings import Settings


def test_version() -> None:
    """The package exposes a version string."""
    assert package_name.__version__


def test_settings_load() -> None:
    """Settings load and inherit CoreSettings fields from core-utils."""
    settings = Settings()
    assert settings.environment  # set to "test" by tests/conftest.py
    assert settings.log_level
