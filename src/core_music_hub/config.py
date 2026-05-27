"""Music hub settings."""

from pathlib import Path

from core_utils.settings import CoreSettings


class MusicSettings(CoreSettings):
    model_config = {
        "env_file": [".env", ".env.local"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow",
    }

    music_host: str = "127.0.0.1"
    music_port: int = 8600
    music_catalog_dir: Path = Path("data/songs")


__all__ = ["MusicSettings"]
