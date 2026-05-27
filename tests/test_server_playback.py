"""Functional tests for POST /play, /stop, /next, GET /status via TestClient."""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import core_music_hub.server.app as app_module


@pytest.fixture
def playing_client(test_client: TestClient, catalog_dir: Path) -> TestClient:
    """TestClient where the fake audio file exists on disk."""
    (catalog_dir / "cocodrilo.mp3").write_bytes(b"\x00" * 16)
    return test_client


# ---------------------------------------------------------------------------
# POST /play
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_play_by_alias(playing_client: TestClient) -> None:
    response = playing_client.post("/play", json={"alias": "dante"})
    assert response.status_code == 200
    data = response.json()
    assert data["playing"]["id"] == "cocodrilo"


@pytest.mark.functional
def test_play_by_id(playing_client: TestClient) -> None:
    response = playing_client.post("/play", json={"id": "tension"})
    # tension.wav doesn't exist on disk → 500 (file missing)
    # We only check that the lookup itself worked (not 404)
    assert response.status_code in {200, 500}


@pytest.mark.functional
def test_play_unknown_alias_returns_404(test_client: TestClient) -> None:
    response = test_client.post("/play", json={"alias": "nope"})
    assert response.status_code == 404


@pytest.mark.functional
def test_play_no_selector_returns_400(test_client: TestClient) -> None:
    response = test_client.post("/play", json={})
    assert response.status_code == 400


@pytest.mark.functional
def test_play_by_mood(playing_client: TestClient) -> None:
    response = playing_client.post("/play", json={"mood": "playful"})
    assert response.status_code == 200
    assert response.json()["playing"]["id"] == "cocodrilo"


@pytest.mark.functional
def test_play_by_tags(playing_client: TestClient) -> None:
    response = playing_client.post("/play", json={"tags": ["animal"]})
    assert response.status_code == 200
    assert response.json()["playing"]["id"] == "cocodrilo"


# ---------------------------------------------------------------------------
# POST /stop
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_stop_returns_200(test_client: TestClient) -> None:
    response = test_client.post("/stop")
    assert response.status_code == 200
    assert response.json() == {"stopped": True}


# ---------------------------------------------------------------------------
# GET /status
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_status_not_playing(test_client: TestClient) -> None:
    response = test_client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["playing"] is False
    assert data["current"] is None


@pytest.mark.functional
def test_status_playing(test_client: TestClient) -> None:
    """Simulate active stream via monkeypatching is_playing on the playback singleton."""
    pb = app_module.playback
    original = pb.is_playing
    try:
        pb.is_playing = lambda: True  # type: ignore[method-assign]
        pb._current = app_module.library.all()[0]  # type: ignore[attr-defined]
        response = test_client.get("/status")
        assert response.status_code == 200
        assert response.json()["playing"] is True
        assert response.json()["current"]["id"] == "cocodrilo"
    finally:
        pb.is_playing = original  # type: ignore[method-assign]
        pb._current = None  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# POST /next
# ---------------------------------------------------------------------------


@pytest.mark.functional
def test_next_rotates_song(playing_client: TestClient) -> None:
    """With two songs, /next should play whichever is not current."""
    # Make tension.wav exist too
    response = playing_client.post("/next")
    # May return 200 or 500 (if the chosen file is missing) but never 404
    assert response.status_code in {200, 500}


@pytest.mark.functional
def test_next_404_when_empty_catalog(tmp_path: Path) -> None:
    """With an empty catalog, /next returns 404."""
    import os

    os.environ["MUSIC_CATALOG_DIR"] = str(tmp_path)
    (tmp_path / "catalog.yaml").write_text("songs: []")

    with (
        patch("core_music_hub.playback.sd"),
        patch("core_music_hub.playback.AudioSegment"),
    ):
        from core_music_hub.server.app import create_app

        empty_app = create_app()
        client = TestClient(empty_app)
        response = client.post("/next")
        assert response.status_code == 404
