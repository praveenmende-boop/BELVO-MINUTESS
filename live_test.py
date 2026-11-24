
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from transcription import transcribe_audio
from live_audio import get_pending_frames, clear_pending_frames
from live_transcription import (
    add_transcription,
    get_live_transcript,
    clear_live_transcript,
    transcribe_audio_frames
)
import time

from live_audio import (
    audio_callback,
    get_recorded_frames,
    clear_recorded_frames,
    save_recording
)

st.set_page_config(
    page_title="BELVO Live Audio Test",
    page_icon="🎙️"
)

st.title("BELVO MINUTES")
st.subheader("Live Microphone Test")

st.write("Start the microphone and speak for a few seconds.")

webrtc_streamer(
    key="belvo-live-test",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=audio_callback,
    media_stream_constraints={
        "video": False,
        "audio": True
    },
    async_processing=True
)


# LIVE TRANSCRIPTION
st.divider()
st.subheader("Live Meeting Transcript")

if st.button("Start Live Transcription"):
    clear_live_transcript()
    clear_pending_frames()
    st.session_state["live_transcription_active"] = True

if st.button("Stop Live Transcription"):
    st.session_state["live_transcription_active"] = False

if st.session_state.get("live_transcription_active", False):
    pending = get_pending_frames(min_frames=300)

    if pending:
        try:
            with st.spinner("Recognizing speech..."):
                text = transcribe_audio_frames(pending)

            add_transcription(text)

        except Exception as e:
            st.error(f"Live transcription error: {e}")

    st.text_area(
        "Recognized Words",
        value=get_live_transcript(),
        height=200,
        key="live_transcript_display"
    )

    time.sleep(0.5)
    st.rerun()
else:
    st.text_area(
        "Recognized Words",
        value=get_live_transcript(),
        height=200,
        disabled=True
    )


frames = get_recorded_frames()

st.write(f"Audio frames captured: {len(frames)}")

if frames:
    st.success("Live microphone audio is being captured!")

if st.button("Clear Test Recording"):
    clear_recorded_frames()
    st.rerun()

if st.button("Save Recording"):
    try:
        recording_path = save_recording(
            "recordings/live_meeting.wav"
        )

        st.success("Recording saved successfully!")

        st.write("Saved at:", recording_path)

    except Exception as e:
        st.error(f"Recording failed: {e}")


if st.button("Generate Transcript"):

    try:
        with st.spinner("BELVO is transcribing your meeting..."):

            result = transcribe_audio(
                "recordings/live_meeting.wav"
            )

        st.success("Transcription completed!")

        st.subheader("Meeting Transcript")

        st.write(result["transcript"])

    except Exception as e:
        st.error(f"Transcription failed: {e}")

