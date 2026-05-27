"""CLI: `python -m core_music_hub` starts the HTTP service."""

import uvicorn

from core_music_hub.config import MusicSettings


def main() -> None:
    settings = MusicSettings()
    uvicorn.run(
        "core_music_hub.server.app:create_app",
        factory=True,
        host=settings.music_host,
        port=settings.music_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
