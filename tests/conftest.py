"""Pytest configuration and shared fixtures."""

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml
from fastapi.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def sample_songs() -> list[dict[str, Any]]:
    return [
        {
            "id": "cocodrilo",
            "title": "El cocodrilo Dante",
            "file": "cocodrilo.mp3",
            "aliases": ["dante", "el cocodrilo"],
            "moods": ["playful", "happy"],
            "tags": ["animal", "classic"],
        },
        {
            "id": "tension",
            "title": "Tension Theme",
            "file": "tension.wav",
            "aliases": ["dramatic"],
            "moods": ["tension"],
            "tags": ["score"],
        },
    ]


@pytest.fixture
def catalog_dir(tmp_path: Path, sample_songs: list[dict[str, Any]]) -> Path:
    """A tmp directory with a populated catalog.yaml."""
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"songs": sample_songs}))
    return tmp_path


@pytest.fixture
def app(catalog_dir: Path) -> Generator[Any, None, None]:
    """FastAPI app initialised with the tmp catalog and mocked audio backends."""
    os.environ["MUSIC_CATALOG_DIR"] = str(catalog_dir)
    with (
        patch("core_music_hub.playback.sd") as mock_sd,
        patch("core_music_hub.playback.AudioSegment") as mock_audio,
    ):
        mock_sd.get_stream.side_effect = Exception("no stream")
        mock_audio.from_file.return_value = _fake_audio_segment()

        from core_music_hub.server.app import create_app

        fastapi_app = create_app()
        yield fastapi_app


@pytest.fixture
def test_client(app: Any) -> TestClient:
    return TestClient(app)


def _fake_audio_segment() -> MagicMock:
    """Return a minimal AudioSegment-like mock."""
    seg = MagicMock()
    seg.channels = 1
    seg.frame_rate = 44100
    seg.get_array_of_samples.return_value = [0] * 1024
    return seg
