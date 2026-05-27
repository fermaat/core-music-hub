"""Non-blocking audio playback engine — pydub for decode, sounddevice for output."""

import threading
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd
from core_utils import logger
from pydub import AudioSegment

from core_music_hub.core.models import Song


class Playback:
    """Single global playback channel.

    Threadsafe: callers can interleave play/stop/status from different request handlers.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current: Song | None = None

    def play(self, song: Song, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        audio: Any = AudioSegment.from_file(file_path)
        samples: np.ndarray[Any, np.dtype[Any]] = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))

        with self._lock:
            sd.stop()
            sd.play(samples, samplerate=audio.frame_rate, blocking=False)
            self._current = song
        logger.info(f"playback: now playing {song.id} ({file_path.name})")

    def stop(self) -> None:
        with self._lock:
            sd.stop()
            self._current = None

    def is_playing(self) -> bool:
        # sd.get_stream() may raise if no stream has been created. Be defensive.
        try:
            stream: Any = sd.get_stream()
        except Exception:
            return False
        return bool(stream and stream.active)

    def current(self) -> Song | None:
        with self._lock:
            if not self.is_playing():
                # Stream finished naturally; surface the truth.
                self._current = None
            return self._current
