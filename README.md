# core-music-hub

HTTP service for local audio playback. Lets clients request playback of audio files
from a local catalog by id, alias, mood, or tags.

Part of the Fante infrastructure stack — sibling of `core-llm-bridge` and
`core-speech-io-hub`.

## Use cases

1. **Jukebox** — `fante` asks the service to play a song by alias  
   (e.g. `{"alias": "el cocodrilo"}` → plays the right track).
2. **Mood score** — narrator requests `{"mood": "tension"}` → service picks a matching song.

## Requirements

- Python 3.12
- `ffmpeg` for MP3 decoding via pydub:
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`

## Quick start

```bash
# Install dependencies
pdm install

# Start the server (default: http://127.0.0.1:8600)
pdm run python -m core_music_hub

# Add songs — see data/songs/README.md for instructions

# Smoke test via CLI
pdm run python -m core_music_hub.cli list
pdm run python -m core_music_hub.cli play <alias>
pdm run python -m core_music_hub.cli status
pdm run python -m core_music_hub.cli stop
```

## HTTP API

| Method | Path       | Description                               |
|--------|------------|-------------------------------------------|
| GET    | /health    | Liveness check                            |
| GET    | /catalog   | List all songs (id, title, aliases, moods, tags) |
| GET    | /status    | Current playback state                    |
| POST   | /play      | Play a song by `id`, `alias`, `mood`, or `tags` |
| POST   | /stop      | Stop playback                             |
| POST   | /next      | Skip to a random other song               |

### Example

```bash
curl -X POST http://127.0.0.1:8600/play \
     -H 'Content-Type: application/json' \
     -d '{"alias": "el cocodrilo"}'

curl http://127.0.0.1:8600/status | python3 -m json.tool
curl -X POST http://127.0.0.1:8600/stop
```

## Configuration

| Env var              | Default         | Description                    |
|----------------------|-----------------|--------------------------------|
| `MUSIC_HOST`         | `127.0.0.1`     | Bind address                   |
| `MUSIC_PORT`         | `8600`          | Bind port                      |
| `MUSIC_CATALOG_DIR`  | `data/songs`    | Path to catalog dir            |
| `ENVIRONMENT`        | `development`   | Inherited from `core-utils`    |
| `LOG_LEVEL`          | `INFO`          | Inherited from `core-utils`    |

Configuration is also read from `.env` / `.env.local` files.

## Development

```bash
make install-dev    # install with dev extras
make check          # ruff + black + mypy + pytest
make test           # pytest only
make format         # auto-format with black
```

## Catalog

Audio files and their YAML index live in `data/songs/`. See
[data/songs/README.md](data/songs/README.md) for instructions on adding songs.
