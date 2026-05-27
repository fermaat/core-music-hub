# Music catalog

This folder holds the audio files this service can play, plus the YAML index that
maps aliases / moods / tags → files.

## Adding a song

1. Drop the file here (MP3/WAV/OGG). Simple filenames, no spaces:
   `cocodrilo_dante.mp3`, `tension_intro.wav`.

2. Add an entry to `catalog.yaml`:

   ```yaml
   songs:
     - id: cocodrilo
       title: "El cocodrilo Dante"
       file: cocodrilo_dante.mp3
       aliases: [dante, "el cocodrilo"]
       moods: [playful, happy]
       tags: [animal, classic]
   ```

3. Restart the server. Hit `GET /catalog` to confirm. `POST /play` with
   `{"alias": "cocodrilo"}` should start playback.

## Requirements

- macOS: `brew install ffmpeg` (pydub uses it for MP3 decoding).
- Linux: `apt install ffmpeg`
- Files should be reasonably short (under 5 min) and at consistent volume.

## Moods worth populating

Suggested taxonomy — extend as needed:

- `calm`, `playful`, `happy`, `sad`, `tension`, `victory`, `mystery`, `sleep`,
  `lullaby`, `adventurous`
