"""Functional tests for MusicHubClient against the TestClient ASGI transport."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core_music_hub.client.client import MusicHubClient, SongNotFoundError


@pytest.fixture
def music_client(test_client: TestClient) -> MusicHubClient:
    """MusicHubClient wired to the in-process TestClient."""
    return MusicHubClient(base_url="http://testserver", _client=test_client)


@pytest.fixture
def music_client_with_files(test_client: TestClient, catalog_dir: Path) -> MusicHubClient:
    """MusicHubClient with fake audio files present on disk."""
    (catalog_dir / "cocodrilo.mp3").write_bytes(b"\x00" * 16)
    (catalog_dir / "tension.wav").write_bytes(b"\x00" * 16)
    return MusicHubClient(base_url="http://testserver", _client=test_client)


# ---------------------------------------------------------------------------
# health()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_health(music_client: MusicHubClient) -> None:
    assert music_client.health() is True


# ---------------------------------------------------------------------------
# catalog()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_catalog_returns_songs(music_client: MusicHubClient) -> None:
    songs = music_client.catalog()
    assert len(songs) == 2
    ids = {s["id"] for s in songs}
    assert ids == {"cocodrilo", "tension"}


# ---------------------------------------------------------------------------
# play()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_play_by_alias(music_client_with_files: MusicHubClient) -> None:
    result = music_client_with_files.play(alias="dante")
    assert result["id"] == "cocodrilo"


@pytest.mark.functional
def test_play_by_id(music_client_with_files: MusicHubClient) -> None:
    result = music_client_with_files.play(id="tension")
    assert result["id"] == "tension"


@pytest.mark.functional
def test_play_by_mood(music_client_with_files: MusicHubClient) -> None:
    result = music_client_with_files.play(mood="playful")
    assert result["id"] == "cocodrilo"


@pytest.mark.functional
def test_play_raises_song_not_found(music_client: MusicHubClient) -> None:
    with pytest.raises(SongNotFoundError):
        music_client.play(alias="nope")


# ---------------------------------------------------------------------------
# stop()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_stop_does_not_raise(music_client: MusicHubClient) -> None:
    music_client.stop()  # should not raise


# ---------------------------------------------------------------------------
# status()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_status_returns_dict(music_client: MusicHubClient) -> None:
    s = music_client.status()
    assert "playing" in s
    assert "current" in s
    assert s["playing"] is False


# ---------------------------------------------------------------------------
# next()
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_next_raises_song_not_found_on_empty_catalog(
    tmp_path: Path,
) -> None:
    import os
    from unittest.mock import patch

    os.environ["MUSIC_CATALOG_DIR"] = str(tmp_path)
    (tmp_path / "catalog.yaml").write_text("songs: []")

    with (
        patch("core_music_hub.playback.sd"),
        patch("core_music_hub.playback.AudioSegment"),
    ):
        from core_music_hub.server.app import create_app

        empty_app = create_app()
        tc = TestClient(empty_app)
        client = MusicHubClient(base_url="http://testserver", _client=tc)
        with pytest.raises(SongNotFoundError):
            client.next()
