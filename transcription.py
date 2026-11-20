
from faster_whisper import WhisperModel
from functools import lru_cache


@lru_cache(maxsize=1)
def load_model():
    print("Loading lightweight Whisper model...")

    return WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8",
        cpu_threads=1,
        num_workers=1
    )


def transcribe_audio(audio_path):

    model = load_model()

    print("Transcribing audio...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=1,
        vad_filter=True
    )

    transcript = []

    for segment in segments:
        transcript.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })

    full_text = " ".join(
        item["text"] for item in transcript
    )

    return {
        "language": info.language,
        "duration": info.duration,
        "transcript": full_text,
        "segments": transcript
    }
