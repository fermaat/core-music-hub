"""Unit tests for the Playback engine — pydub and sounddevice are mocked."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core_music_hub.core.models import Song
from core_music_hub.playback import Playback


@pytest.fixture
def song(tmp_path: Path) -> Song:
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"\x00" * 16)  # fake audio bytes
    return Song(id="test", title="Test Song", file="test.mp3")


@pytest.fixture
def song_path(tmp_path: Path, song: Song) -> Path:
    return tmp_path / song.file


def _fake_segment(channels: int = 1) -> MagicMock:
    seg = MagicMock()
    seg.channels = channels
    seg.frame_rate = 44100
    seg.get_array_of_samples.return_value = [0] * 1024
    return seg


# ---------------------------------------------------------------------------
# play()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_play_calls_sd_play(song: Song, song_path: Path) -> None:
    with (
        patch("core_music_hub.playback.AudioSegment") as mock_audio,
        patch("core_music_hub.playback.sd") as mock_sd,
        patch("core_music_hub.playback.np.array") as mock_np,
    ):
        mock_audio.from_file.return_value = _fake_segment()
        mock_np.return_value = MagicMock()
        mock_sd.get_stream.side_effect = Exception("no stream")

        pb = Playback()
        pb.play(song, song_path)

        mock_sd.stop.assert_called()
        mock_sd.play.assert_called_once()
        assert pb.current() is None  # is_playing returns False (no stream)


@pytest.mark.unit
def test_play_stereo_reshapes_samples(song: Song, song_path: Path) -> None:
    with (
        patch("core_music_hub.playback.AudioSegment") as mock_audio,
        patch("core_music_hub.playback.sd"),
    ):
        seg = _fake_segment(channels=2)
        mock_audio.from_file.return_value = seg

        pb = Playback()
        pb.play(song, song_path)

        # get_array_of_samples was called (reshape happens after)
        seg.get_array_of_samples.assert_called_once()


@pytest.mark.unit
def test_play_raises_if_file_missing(song: Song, tmp_path: Path) -> None:
    pb = Playback()
    with pytest.raises(FileNotFoundError):
        pb.play(song, tmp_path / "does_not_exist.mp3")


# ---------------------------------------------------------------------------
# stop()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stop_calls_sd_stop() -> None:
    with patch("core_music_hub.playback.sd") as mock_sd:
        pb = Playback()
        pb.stop()
        mock_sd.stop.assert_called_once()


@pytest.mark.unit
def test_stop_clears_current(song: Song, song_path: Path) -> None:
    with (
        patch("core_music_hub.playback.AudioSegment") as mock_audio,
        patch("core_music_hub.playback.sd") as mock_sd,
        patch("core_music_hub.playback.np.array") as mock_np,
    ):
        mock_audio.from_file.return_value = _fake_segment()
        mock_np.return_value = MagicMock()
        # Simulate active stream while playing, then stop
        mock_sd.get_stream.return_value = MagicMock(active=True)

        pb = Playback()
        pb.play(song, song_path)
        # Manually set _current to simulate it was set
        pb._current = song

        mock_sd.get_stream.side_effect = Exception("no stream")
        pb.stop()
        assert pb._current is None


# ---------------------------------------------------------------------------
# is_playing() / current()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_is_playing_false_when_no_stream() -> None:
    with patch("core_music_hub.playback.sd") as mock_sd:
        mock_sd.get_stream.side_effect = Exception("no stream")
        pb = Playback()
        assert pb.is_playing() is False


@pytest.mark.unit
def test_is_playing_true_when_stream_active() -> None:
    with patch("core_music_hub.playback.sd") as mock_sd:
        mock_sd.get_stream.return_value = MagicMock(active=True)
        pb = Playback()
        assert pb.is_playing() is True


@pytest.mark.unit
def test_current_returns_none_when_not_playing() -> None:
    with patch("core_music_hub.playback.sd") as mock_sd:
        mock_sd.get_stream.side_effect = Exception("no stream")
        pb = Playback()
        assert pb.current() is None
