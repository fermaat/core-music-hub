"""GET /catalog — list all songs (stripped of internal-only fields)."""

from typing import Any

from fastapi import APIRouter

from core_music_hub.core.models import CatalogEntry

router = APIRouter()


@router.get("/catalog")
def catalog() -> dict[str, Any]:
    from core_music_hub.server.app import library  # late import to share state

    entries = [
        CatalogEntry(
            id=s.id, title=s.title, aliases=s.aliases, moods=s.moods, tags=s.tags
        ).model_dump()
        for s in library.all()
    ]
    return {"songs": entries}
