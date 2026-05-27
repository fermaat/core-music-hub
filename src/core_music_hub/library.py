"""Library — loads the YAML catalog and supports lookup by id/alias/mood/tags."""

import random
import unicodedata
from pathlib import Path

import yaml

from core_music_hub.core.models import Song


def _normalize(s: str) -> str:
    nfd = unicodedata.normalize("NFD", s.lower().strip())
    flat = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return " ".join(flat.split())


class SongNotFoundError(LookupError):
    """Raised when no song matches the play request."""


class Library:
    def __init__(self, songs: list[Song], root: Path) -> None:
        self._songs = list(songs)
        self._root = root
        self._by_key: dict[str, Song] = {}
        for song in self._songs:
            for key in (song.id, *song.aliases):
                self._by_key[_normalize(key)] = song

    @classmethod
    def from_directory(cls, path: Path) -> "Library":
        catalog = path / "catalog.yaml"
        if not catalog.exists():
            return cls(songs=[], root=path)
        with catalog.open() as f:
            data = yaml.safe_load(f) or {}
        songs = [Song(**s) for s in (data.get("songs") or [])]
        return cls(songs=songs, root=path)

    def root(self) -> Path:
        return self._root

    def all(self) -> list[Song]:
        return list(self._songs)

    def by_id_or_alias(self, key: str) -> Song:
        normalized = _normalize(key)
        if normalized not in self._by_key:
            raise SongNotFoundError(f"No song matches alias/id {key!r}")
        return self._by_key[normalized]

    def by_mood(self, mood: str, rng: random.Random | None = None) -> Song:
        rng = rng or random.Random()
        m = _normalize(mood)
        candidates = [s for s in self._songs if any(_normalize(x) == m for x in s.moods)]
        if not candidates:
            raise SongNotFoundError(f"No song matches mood {mood!r}")
        return rng.choice(candidates)

    def by_tags(self, tags: list[str], rng: random.Random | None = None) -> Song:
        rng = rng or random.Random()
        normalized = {_normalize(t) for t in tags}
        candidates = [s for s in self._songs if normalized & {_normalize(t) for t in s.tags}]
        if not candidates:
            raise SongNotFoundError(f"No song matches any of tags {tags}")
        return rng.choice(candidates)

    def file_path(self, song: Song) -> Path:
        return self._root / song.file
