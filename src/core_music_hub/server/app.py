"""FastAPI application factory + global runtime state."""

from fastapi import FastAPI

from core_music_hub.config import MusicSettings
from core_music_hub.library import Library
from core_music_hub.playback import Playback
from core_music_hub.server.routes.catalog import router as catalog_router
from core_music_hub.server.routes.health import router as health_router
from core_music_hub.server.routes.playback import router as playback_router

# Module-level singletons — initialised in create_app(). Routes pull from here
# via late imports to avoid circular deps.
library: Library
playback: Playback


def create_app() -> FastAPI:
    global library, playback
    settings = MusicSettings()
    library = Library.from_directory(settings.music_catalog_dir)
    playback = Playback()

    app = FastAPI(title="core-music-hub", version="0.1.0")
    app.include_router(health_router)
    app.include_router(catalog_router)
    app.include_router(playback_router)
    return app
