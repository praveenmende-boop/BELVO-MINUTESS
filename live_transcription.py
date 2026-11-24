
import threading

# Stores completed transcription chunks
transcription_chunks = []

# Prevents conflicts between background processing and the app
transcription_lock = threading.Lock()


def add_transcription(text):
    """Add a newly transcribed audio chunk."""
    if not text or not text.strip():
        return

    with transcription_lock:
        transcription_chunks.append(text.strip())


def get_live_transcript():
    """Return all completed transcription chunks."""
    with transcription_lock:
        return " ".join(transcription_chunks)


def clear_live_transcript():
    """Clear the transcript before a new meeting."""
    with transcription_lock:
        transcription_chunks.clear()



import av
import numpy as np
import wave
import tempfile
import os

from transcription import transcribe_audio


def transcribe_audio_frames(frames):
    """Convert audio frames to WAV and transcribe them."""

    if not frames:
        return ""

    resampler = av.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000
    )

    audio_chunks = []

    for frame in frames:
        converted_frames = resampler.resample(frame)

        for converted in converted_frames:
            audio_chunks.append(converted.to_ndarray())

    remaining = resampler.resample(None)

    for converted in remaining:
        audio_chunks.append(converted.to_ndarray())

    if not audio_chunks:
        return ""

    audio_data = np.concatenate(audio_chunks, axis=1)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:
            temp_path = temp_file.name

        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data.tobytes())

        result = transcribe_audio(temp_path)

        return result["transcript"]

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

