
import os
import tempfile
from pathlib import Path
from typing import Optional

import pyttsx3


_whisper_model = None


def transcribe_audio(
    audio_bytes: bytes,
    model_size: str = "base",
    language: Optional[str] = "en",
) -> str:
    """
    Transcribe recorded audio using faster-whisper locally.

    The first invocation may download the selected model if it
    is not already cached.
    """
    global _whisper_model

    if not audio_bytes:
        raise ValueError("No audio data was supplied.")

    from faster_whisper import WhisperModel

    if _whisper_model is None:
        _whisper_model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

    audio_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as audio_file:
            audio_file.write(audio_bytes)
            audio_path = audio_file.name

        segments, _ = _whisper_model.transcribe(
            audio_path,
            language=language,
            vad_filter=True,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


def generate_speech_file(
    text: str,
    output_path: str = None,
) -> str:
    """
    Generate a speech file using the computer's installed voice.

    Returns the path of the generated WAV file.
    """
    if not text or not text.strip():
        raise ValueError("Text to speak cannot be empty.")

    if output_path is None:
        handle = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        )
        output_path = handle.name
        handle.close()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    engine = pyttsx3.init()

    try:
        engine.setProperty("rate", 165)
        engine.save_to_file(text.strip(), str(output))
        engine.runAndWait()
    finally:
        engine.stop()

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(
            "Speech audio was not generated. Check system voice support."
        )

    return str(output)
