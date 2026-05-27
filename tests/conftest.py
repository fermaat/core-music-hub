"""Pytest configuration and shared fixtures."""

import os
from pathlib import Path

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent
