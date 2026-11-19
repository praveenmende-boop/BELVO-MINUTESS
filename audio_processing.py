
import os
import subprocess
import imageio_ffmpeg


def process_audio(input_path, output_path):

    if not os.path.exists(input_path):
        raise FileNotFoundError("Input audio file not found.")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-1000:])

    return output_path
