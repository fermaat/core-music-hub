"""POST /play, POST /stop, POST /next, GET /status."""

import random
from typing import Any

from fastapi import APIRouter, HTTPException

from core_music_hub.core.models import PlayRequest, PlayStatus, Song
from core_music_hub.library import SongNotFoundError

router = APIRouter()


def _select_song(req: PlayRequest) -> Song:
    from core_music_hub.server.app import library

    if req.id is not None:
        return library.by_id_or_alias(req.id)
    if req.alias is not None:
        return library.by_id_or_alias(req.alias)
    if req.mood is not None:
        return library.by_mood(req.mood)
    if req.tags is not None and req.tags:
        return library.by_tags(req.tags)
    raise HTTPException(400, "Provide exactly one of id, alias, mood, or tags")


@router.post("/play")
def play(req: PlayRequest) -> dict[str, Any]:
    from core_music_hub.server.app import library, playback

    try:
        song = _select_song(req)
        playback.play(song, library.file_path(song))
    except SongNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(500, f"Audio file missing on disk: {exc}") from exc
    return {"playing": song.model_dump()}


@router.post("/stop")
def stop() -> dict[str, bool]:
    from core_music_hub.server.app import playback

    playback.stop()
    return {"stopped": True}


@router.post("/next")
def next_song() -> dict[str, Any]:
    from core_music_hub.server.app import library, playback

    current = playback.current()
    candidates = [s for s in library.all() if s != current]
    if not candidates:
        raise HTTPException(404, "No other songs available")
    chosen = random.choice(candidates)
    try:
        playback.play(chosen, library.file_path(chosen))
    except FileNotFoundError as exc:
        raise HTTPException(500, f"Audio file missing on disk: {exc}") from exc
    return {"playing": chosen.model_dump()}


@router.get("/status")
def status() -> dict[str, Any]:
    from core_music_hub.server.app import playback

    return PlayStatus(playing=playback.is_playing(), current=playback.current()).model_dump()
