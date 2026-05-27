# core-music-hub — Summary

## Purpose

Small Python library + HTTP service that lets clients request playback of audio
files from a local catalog. Songs can be requested by id, alias, mood, or tags.
Downstream consumer: **fante** (jukebox mode + mood-driven score).

## Architecture

```
core-music-hub/
├── src/core_music_hub/
│   ├── __init__.py          version string
│   ├── __main__.py          entry point → uvicorn on port 8600
│   ├── cli.py               smoke CLI: list / play / stop / status
│   ├── config.py            MusicSettings (CoreSettings subclass)
│   ├── library.py           Library — loads YAML catalog, lookup by id/alias/mood/tags
│   ├── playback.py          Playback — non-blocking pydub + sounddevice engine
│   ├── core/
│   │   └── models.py        Song, PlayRequest, PlayStatus, CatalogEntry (Pydantic)
│   ├── server/
│   │   ├── app.py           create_app() factory; global library + playback singletons
│   │   └── routes/
│   │       ├── health.py    GET /health
│   │       ├── catalog.py   GET /catalog
│   │       └── playback.py  POST /play, /stop, /next; GET /status
│   └── client/
│       └── client.py        MusicHubClient — httpx wrapper for the HTTP API
├── data/songs/
│   ├── catalog.yaml         YAML index of songs (id, aliases, moods, tags, file)
│   └── README.md            how to add songs
└── tests/
    ├── conftest.py          fixtures: catalog_dir, app (mocked audio), test_client
    ├── test_library.py      unit — Library lookup / normalization
    ├── test_playback.py     unit — Playback (mocked sd + pydub)
    ├── test_server_catalog.py  functional — GET /health, /catalog via TestClient
    ├── test_server_playback.py functional — POST /play, /stop, /next, GET /status
    └── test_client.py       functional — MusicHubClient end-to-end via TestClient
```

## Key classes

| Class | Location | Purpose |
|---|---|---|
| `Song` | `core/models.py` | Pydantic model: id, title, file, aliases, moods, tags |
| `PlayRequest` | `core/models.py` | Union selector: id \| alias \| mood \| tags |
| `PlayStatus` | `core/models.py` | Playback state: playing bool + current Song |
| `CatalogEntry` | `core/models.py` | Public catalog view (no `file` field) |
| `Library` | `library.py` | Load YAML catalog; lookup by id/alias (normalized), mood, tags |
| `Playback` | `playback.py` | Thread-safe play/stop/is_playing/current via sounddevice |
| `MusicSettings` | `config.py` | `music_host`, `music_port`, `music_catalog_dir` |
| `MusicHubClient` | `client/client.py` | Python HTTP client for all endpoints |

## Entry points

```python
# Start server
# python -m core_music_hub

# Use client in code
from core_music_hub.client.client import MusicHubClient

client = MusicHubClient()          # defaults to http://127.0.0.1:8600
client.health()                    # → True
client.catalog()                   # → list[dict]
client.play(alias="el cocodrilo")  # → {"id": ..., "title": ...}
client.status()                    # → {"playing": True, "current": {...}}
client.stop()
client.next()
```

## Configuration

| Env var             | Default       |
|---------------------|---------------|
| `MUSIC_HOST`        | `127.0.0.1`   |
| `MUSIC_PORT`        | `8600`        |
| `MUSIC_CATALOG_DIR` | `data/songs`  |

Also reads `.env` / `.env.local`.

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | HTTP framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data models |
| `httpx` | HTTP client (MusicHubClient + tests) |
| `pyyaml` | Catalog YAML parsing |
| `pydub` | Audio file decoding (needs ffmpeg for MP3) |
| `sounddevice` | Low-latency audio output via PortAudio |
| `numpy` | Audio sample array conversion |
| `core-utils` | CoreSettings, logger |

## Phase status

- **Phase 0** ✅ — Bootstrap: all modules, HTTP API, client, tests, mocked audio in CI
- **Phase 1** ⏳ — Crossfade, volume control, EQ (out of scope for V1)
- **Phase 2** ⏳ — Auto-next when song ends naturally

## Consumers / upstream

- **fante** → uses `MusicHubClient` to request playback
- **core-utils** → provides `CoreSettings`, `logger`
