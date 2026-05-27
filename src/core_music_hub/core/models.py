"""Shared domain types for the music hub."""

from pydantic import BaseModel, Field


class Song(BaseModel):
    """A single song entry."""

    id: str  # canonical id, also implicit alias
    title: str  # human-readable
    file: str  # filename (relative to catalog dir)
    aliases: list[str] = Field(default_factory=list)
    moods: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PlayRequest(BaseModel):
    """A play request — exactly one of (id, alias, mood, tags) should be set."""

    id: str | None = None
    alias: str | None = None
    mood: str | None = None
    tags: list[str] | None = None


class PlayStatus(BaseModel):
    """Current playback state."""

    playing: bool
    current: Song | None = None


class CatalogEntry(BaseModel):
    """Song stripped of internal-only fields (none today; future-proofing)."""

    id: str
    title: str
    aliases: list[str]
    moods: list[str]
    tags: list[str]
