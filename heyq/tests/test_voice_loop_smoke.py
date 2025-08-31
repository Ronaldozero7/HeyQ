from __future__ import annotations
import pytest

try:
    from heyq.voice.voice_interface import VoiceInterface, sr  # type: ignore
except Exception:  # pragma: no cover - if import fails due to SpeechRecognition
    VoiceInterface = None  # type: ignore
    sr = None  # type: ignore


@pytest.mark.smoke
def test_voice_interface_init():
    if sr is None or VoiceInterface is None:
        pytest.skip("SpeechRecognition not available; skipping voice smoke test")
    vi = VoiceInterface()
    assert vi is not None
