
import threading
import av
import numpy as np
import wave
import os

# Stores audio frames captured during the meeting
audio_frames = []
audio_lock = threading.Lock()



def audio_callback(frame):
    """Collect audio for recording and live transcription."""

    with audio_lock:
        audio_frames.append(frame)

    add_pending_frame(frame)

    return frame



def get_recorded_frames():
    """Return the collected audio frames safely."""
    with audio_lock:
        return list(audio_frames)


def clear_recorded_frames():
    """Clear previous meeting audio."""
    with audio_lock:
        audio_frames.clear()

def save_recording(output_path):
    """Convert captured audio frames into a 16 kHz mono WAV file."""

    frames = get_recorded_frames()

    if not frames:
        raise ValueError("No audio frames were captured.")

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

    # Flush any remaining audio samples
    remaining = resampler.resample(None)

    for converted in remaining:
        audio_chunks.append(converted.to_ndarray())

    if not audio_chunks:
        raise ValueError("Audio conversion produced no samples.")

    audio_data = np.concatenate(audio_chunks, axis=1)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(audio_data.tobytes())

    return output_path


# Stores audio frames waiting for transcription
pending_frames = []
pending_lock = threading.Lock()


def add_pending_frame(frame):
    """Add a frame to the live transcription queue."""
    with pending_lock:
        pending_frames.append(frame)


def get_pending_frames(min_frames=100):
    """Get audio only when enough frames are available."""
    with pending_lock:
        if len(pending_frames) < min_frames:
            return []

        frames = list(pending_frames)
        pending_frames.clear()

    return frames

def clear_pending_frames():
    """Clear audio waiting for transcription."""
    with pending_lock:
        pending_frames.clear()

