
from faster_whisper import WhisperModel


def transcribe_audio(audio_path):

    print("Loading AI transcription model...")

    # Load a locally running speech recognition model
    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

    print("Transcribing audio...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
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
