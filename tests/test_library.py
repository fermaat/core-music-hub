"""Unit tests for the Library class."""

import random
from pathlib import Path
from typing import Any

import pytest
import yaml

from core_music_hub.core.models import Song
from core_music_hub.library import Library, SongNotFoundError


@pytest.fixture
def populated_library(tmp_path: Path, sample_songs: list[dict[str, Any]]) -> Library:
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"songs": sample_songs}))
    return Library.from_directory(tmp_path)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_from_directory_loads_songs(populated_library: Library) -> None:
    assert len(populated_library.all()) == 2


@pytest.mark.unit
def test_from_directory_empty_when_no_catalog(tmp_path: Path) -> None:
    lib = Library.from_directory(tmp_path)
    assert lib.all() == []


@pytest.mark.unit
def test_from_directory_empty_songs_key(tmp_path: Path) -> None:
    (tmp_path / "catalog.yaml").write_text("songs: []")
    lib = Library.from_directory(tmp_path)
    assert lib.all() == []


# ---------------------------------------------------------------------------
# Lookup by id / alias
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_by_id(populated_library: Library) -> None:
    song = populated_library.by_id_or_alias("cocodrilo")
    assert song.id == "cocodrilo"


@pytest.mark.unit
def test_by_alias(populated_library: Library) -> None:
    song = populated_library.by_id_or_alias("dante")
    assert song.id == "cocodrilo"


@pytest.mark.unit
def test_by_alias_case_insensitive(populated_library: Library) -> None:
    song = populated_library.by_id_or_alias("DANTE")
    assert song.id == "cocodrilo"


@pytest.mark.unit
def test_by_alias_accent_insensitive(populated_library: Library) -> None:
    # "el cocodrilo" stored with accent-stripped normalization
    song = populated_library.by_id_or_alias("El Cocodrilo")
    assert song.id == "cocodrilo"


@pytest.mark.unit
def test_by_alias_not_found(populated_library: Library) -> None:
    with pytest.raises(SongNotFoundError):
        populated_library.by_id_or_alias("unknown")


# ---------------------------------------------------------------------------
# Lookup by mood
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_by_mood_returns_matching_song(populated_library: Library) -> None:
    song = populated_library.by_mood("tension")
    assert song.id == "tension"


@pytest.mark.unit
def test_by_mood_case_insensitive(populated_library: Library) -> None:
    song = populated_library.by_mood("PLAYFUL")
    assert song.id == "cocodrilo"


@pytest.mark.unit
def test_by_mood_not_found(populated_library: Library) -> None:
    with pytest.raises(SongNotFoundError):
        populated_library.by_mood("epic")


@pytest.mark.unit
def test_by_mood_uses_rng(populated_library: Library) -> None:
    # Both songs have "playful" would require more data; just check determinism
    rng = random.Random(42)
    song = populated_library.by_mood("happy", rng=rng)
    assert song.id == "cocodrilo"


# ---------------------------------------------------------------------------
# Lookup by tags
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_by_tags_returns_matching_song(populated_library: Library) -> None:
    song = populated_library.by_tags(["score"])
    assert song.id == "tension"


@pytest.mark.unit
def test_by_tags_partial_overlap(populated_library: Library) -> None:
    # "classic" only matches cocodrilo
    song = populated_library.by_tags(["classic", "score"], rng=random.Random(0))
    assert song.id in {"cocodrilo", "tension"}


@pytest.mark.unit
def test_by_tags_not_found(populated_library: Library) -> None:
    with pytest.raises(SongNotFoundError):
        populated_library.by_tags(["nonexistent"])


# ---------------------------------------------------------------------------
# file_path helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_file_path(tmp_path: Path) -> None:
    song = Song(id="x", title="X", file="x.mp3")
    lib = Library(songs=[song], root=tmp_path)
    assert lib.file_path(song) == tmp_path / "x.mp3"
