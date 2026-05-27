"""Functional tests for GET /catalog and GET /health via TestClient."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.functional
def test_health(test_client: TestClient) -> None:
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.functional
def test_catalog_returns_all_songs(test_client: TestClient) -> None:
    response = test_client.get("/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "songs" in data
    assert len(data["songs"]) == 2


@pytest.mark.functional
def test_catalog_song_fields(test_client: TestClient) -> None:
    response = test_client.get("/catalog")
    songs: list[dict[str, Any]] = response.json()["songs"]
    ids = {s["id"] for s in songs}
    assert ids == {"cocodrilo", "tension"}


@pytest.mark.functional
def test_catalog_entry_has_expected_fields(test_client: TestClient) -> None:
    response = test_client.get("/catalog")
    song = next(s for s in response.json()["songs"] if s["id"] == "cocodrilo")
    assert song["title"] == "El cocodrilo Dante"
    assert "dante" in song["aliases"]
    assert "playful" in song["moods"]
    assert "animal" in song["tags"]


@pytest.mark.functional
def test_catalog_no_file_field_exposed(test_client: TestClient) -> None:
    """CatalogEntry strips the internal 'file' field."""
    response = test_client.get("/catalog")
    for song in response.json()["songs"]:
        assert "file" not in song
