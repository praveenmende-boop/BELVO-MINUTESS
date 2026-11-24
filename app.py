
from typing import Any

import streamlit as st
import os
from datetime import datetime
from audio_processing import process_audio
from transcription import transcribe_audio
from name_tracker import track_name_mentions
from summarization import summarize_meeting
from decision_extraction import extract_decisions
from action_items import extract_action_items
from pdf_report import generate_meeting_pdf
from streamlit_webrtc import webrtc_streamer, WebRtcMode

from live_audio import (
    audio_callback,
    get_recorded_frames,
    clear_recorded_frames,
    save_recording
)

 

#Application configuration


# Create required folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed_audio", exist_ok=True)

# Application header
st.title("🎙️ BELVO MINUTES")
st.markdown("---")
st.header("🎧 Live Meeting")
st.write("Record a meeting directly using your microphone.")

live_meeting_name = st.text_input(
    "Live Meeting Name",
    placeholder="Enter meeting name"
)
live_person_name = st.text_input(
    "Name to Track",
    placeholder="Enter the name to track"
)
live_name_variations = st.text_input(
    "Name Variations",
    placeholder="Enter variations separated by commas"
)

if "live_recording_saved" not in st.session_state:
    st.session_state["live_recording_saved"] = False


if "live_recording_saved" not in st.session_state:
    st.session_state["live_recording_saved"] = False

if "live_recording_active" not in st.session_state:
    st.session_state["live_recording_active"] = False

# Custom BELVO recording controls
st.subheader("🎙️ Recording Controls")

if not st.session_state["live_recording_active"]:
    if st.button("▶️ START RECORDING", key="belvo_start"):
        clear_recorded_frames()
        st.session_state["live_recording_active"] = True
else:
    if st.button("⏹️ STOP RECORDING", key="belvo_stop"):
        st.session_state["live_recording_active"] = False

# WebRTC audio connection
ctx = webrtc_streamer(
    key="belvo_live_meeting",
    mode=WebRtcMode.SENDONLY,
    desired_playing_state=st.session_state["live_recording_active"],
    audio_receiver_size=1024,
    media_stream_constraints={
        "video": False,
        "audio": True
    },
    audio_frame_callback=audio_callback,
)

if ctx.state.playing:
    st.success("Microphone is active. Your meeting is being recorded.")
elif st.session_state["live_recording_active"]:
    st.info("Connecting to your microphone...")
else:
    st.info("Recording is stopped. You can save your recording below.")


if ctx.state.playing:
    st.success("Microphone is active. Your meeting is being recorded.")
else:
    st.info("Click START to begin recording and STOP to finish.")

if st.button("💾 Save Live Recording"):
    frames = get_recorded_frames()

    if frames:
        live_audio_path = os.path.join(
            "uploads",
            f"live_meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )
        save_recording(live_audio_path)
        st.session_state["live_audio_path"] = live_audio_path
        st.session_state["live_recording_saved"] = True
        st.success("Live meeting recording saved successfully!")
    else:
        st.warning("No audio recorded. Please start a meeting first.")

if st.button("📝 Transcribe Live Meeting"):
    live_audio_path: Any | None = st.session_state.get("live_audio_path")

    if live_audio_path and os.path.exists(live_audio_path):
        with st.spinner("Transcribing your meeting... Please wait."):
           live_result = transcribe_audio(live_audio_path)

           st.session_state["live_transcript"] = live_result["transcript"]
           st.session_state["live_segments"] = live_result["segments"]
           st.session_state["live_language"] = live_result["language"]
        st.success("Transcription completed!")
    else:
        st.warning("Please save your live recording first.")

if "live_transcript" in st.session_state:
    st.subheader("📄 Live Meeting Transcript")
    st.write(
        f"Detected Language: {st.session_state.get('live_language', 'Unknown')}"
    )
    st.text_area(
        "Meeting Transcript",
        value=st.session_state["live_transcript"],
        height=300
    )

    if st.button("✨ Generate Meeting Summary"):
        transcript = st.session_state["live_transcript"]

        with st.spinner("Generating meeting insights..."):
            live_summary = summarize_meeting(transcript)
            live_decisions = extract_decisions(transcript)
            live_action_items = extract_action_items(transcript)

        st.session_state["live_summary"] = live_summary
        st.session_state["live_decisions"] = live_decisions
        st.session_state["live_action_items"] = live_action_items
        st.success("Meeting insights generated successfully!")

    if "live_summary" in st.session_state:
        live_name_mentions = []
        if live_person_name.strip():
            live_name_mentions = track_name_mentions(
                st.session_state["live_segments"],
                live_person_name,
                [
                    name.strip()
                    for name in live_name_variations.split(",")
                    if name.strip()
                ]
            )

        st.subheader("📌 AI Meeting Summary")
        st.write(st.session_state["live_summary"])

        st.subheader("✅ Key Decisions")
        st.write(st.session_state["live_decisions"])

        st.subheader("📋 Action Items")
        st.write(st.session_state["live_action_items"])

        st.subheader("🔎 Name Mention Tracker")
        if live_person_name.strip():
            if live_name_mentions:
                st.write(live_name_mentions)
            else:
                st.info("No mentions found.")
        else:
            st.info("Enter a name above to activate name tracking.")

        if st.button("📄 Generate Live Meeting PDF"):
            report_path = generate_meeting_pdf(
                meeting_name=live_meeting_name or "Live Meeting",
                transcript=st.session_state["live_transcript"],
                summary=st.session_state["live_summary"],
                decisions=st.session_state["live_decisions"],
                action_items=st.session_state["live_action_items"],
                name_mentions=live_name_mentions,
                tracked_name=live_person_name
            )

            st.success("PDF report generated successfully!")
            with open(report_path, "rb") as pdf_file:
                st.download_button(
                    label="⬇️ Download Meeting Report",
                    data=pdf_file,
                    file_name="BELVO_Live_Meeting_Report.pdf",
                    mime="application/pdf",
                    key="download_live_meeting_report"
                )

st.divider()
st.subheader("AI-Powered Meeting Intelligence Platform")

st.write(
    "Upload your meeting recording to generate "
    "transcripts, summaries, decisions and action items."
)

st.divider()

# Meeting upload section
st.header("📁 Upload Meeting Recording")
person_name = st.text_input(
    "Enter the name to track",
    placeholder="Example: Praveen"
)

name_variations = st.text_input(
    "Other name variations (optional, comma-separated)",
    placeholder="Example: Praveen, Pravin"
)

meeting_name = st.text_input(
    "Meeting Name",
    placeholder="Example: Weekly Team Meeting"
)
uploaded_file = st.file_uploader(
    "Upload Audio or Video File",
    type=[
        "mp3", "wav", "m4a", "ogg",
        "mp4", "mov", "avi", "mkv"
    ]
)
if uploaded_file is not None:
    video_extensions = ["mp4", "mov", "avi", "mkv"]
    file_extension = uploaded_file.name.split(".")[-1].lower()

    is_video = file_extension in video_extensions

    st.success("UploadFile selected successfully!")

    st.write("File:", uploaded_file.name)
    st.write("Size:", round(uploaded_file.size / 1024, 2), "KB")

    if is_video:
        st.video(uploaded_file)
    else:
        st.audio(uploaded_file)

    if st.button("Save Meeting Recording"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join("uploads", filename)

        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        st.success("Meeting recording saved successfully!")
        st.write("Saved location:", file_path)

        processed_path = os.path.join(
            "processed_audio",
            os.path.splitext(filename)[0] + ".wav"
        )

        try:
            process_audio(file_path, processed_path)

            st.success("Audio processing completed!")
            st.audio(processed_path)

            # AI Transcription
            st.subheader("🤖 AI Meeting Transcription")

            with st.spinner("AI is listening to your meeting..."):
                result = transcribe_audio(processed_path)

            st.success("Transcription completed!")
            st.write("Detected Language:", result["language"])

            st.text_area(
                "Meeting Transcript",
                result["transcript"],
                height=250
            )

            # Name Mention Tracker
            variations = [
                item.strip()
                for item in name_variations.split(",")
                if item.strip()
            ]

            name_mentions = track_name_mentions(
                result["segments"],
                person_name,
                variations
            )

            st.divider()
            st.subheader("🔎 Name Mention Tracker")

            if person_name.strip():
                if name_mentions:
                    st.success(
                        f"Found {len(name_mentions)} mention(s) "
                        f"of {person_name}!"
                    )

                    for mention in name_mentions:
                        seconds = int(mention["timestamp"])
                        timestamp = f"{seconds // 60:02d}:{seconds % 60:02d}"

                        st.write(f"**Timestamp:** {timestamp}")
                        st.write(f"**Context:** {mention['context']}" )
                        st.divider()
                else:
                    st.info("No mentions of this name were detected.")
            else:
                st.info("Enter a name above to activate name tracking.")

            transcript_path = os.path.join(
                "processed_audio",
                os.path.splitext(filename)[0] + ".txt"
            )

            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(result["transcript"])

            st.success("Transcript saved successfully!")

            st.divider()
            st.subheader("📝 AI Meeting Summary")

            with st.spinner("Generating meeting summary..."):
                summary = summarize_meeting(result["transcript"])

            st.success("Meeting summary generated!")
            st.write(summary)

            st.divider()
            st.subheader("🎯 Key Meeting Decisions")

            decisions = extract_decisions(result["transcript"])

            if decisions:
                for index, decision in enumerate(decisions, start=1):
                    st.write(f"**Decision {index}:** {decision}")
            else:
                st.info("No clear decisions detected in this meeting.")

            st.divider()
            st.subheader("📌 Meeting Action Items")

            action_items = extract_action_items(result["transcript"])

            if action_items:
                for index, item in enumerate(action_items, start=1):
                    st.write(f"**Task {index}:** {item}")
            else:
                st.info("No action items detected in this meeting.")

            st.session_state["meeting_report_data"] = {
                "meeting_name": meeting_name or "Untitled Meeting",
                "transcript": result["transcript"],
                "summary": summary,
                "decisions": decisions,
                "action_items": action_items,
                "name_mentions": name_mentions,
                "tracked_name": person_name,
            }

        except Exception as e:
            st.error(f"Processing failed: {e}")

else:
    st.info("Please upload an audio recording to continue.")

st.divider()
st.subheader("📄 BELVO MINUTES - PDF Report")

report_data = st.session_state.get("meeting_report_data")
if report_data:
    try:
        report_path = generate_meeting_pdf(
              meeting_name=report_data["meeting_name"],
              transcript=report_data["transcript"],
              summary=report_data["summary"],
              decisions=report_data["decisions"],
              action_items=report_data["action_items"],
              name_mentions=report_data.get("name_mentions", []),
              tracked_name=report_data.get("tracked_name", "")
)
        with open(report_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Download Meeting Report",
                data=pdf_file.read(),
                file_name="BELVO_Meeting_Report.pdf",
                mime="application/pdf",
                key="download_meeting_report"
            )

    except Exception as e:
        st.error(f"PDF Error: {e}")
else:
    st.info("Process a recording to generate a PDF report.")

st.divider()

st.caption("“Every Meeting Matters. Every Minute Counts.”")

# Create required folders

# Custom BELVO MINUTES Dashboard Styling


# ---------------- CUSTOM STYLING ----------------

st.markdown("""
<style>

/* BELVO PREMIUM DARK GLASS THEME */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background:
        radial-gradient(circle at 10% 10%, rgba(117,69,232,0.22), transparent 35%),
        radial-gradient(circle at 90% 85%, rgba(50,124,235,0.20), transparent 35%),
        linear-gradient(135deg, #080D1A, #111A35, #171936) !important;
}

/* Main text */
.stApp p,
.stApp label,
.stApp li,
.stApp [data-testid="stMarkdownContainer"],
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #F1F2FF !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: rgba(255,255,255,0.07) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(167,139,250,0.35) !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #AEB6D0 !important;
}

/* Input focus */
.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #9B7BFF !important;
    box-shadow: 0 0 12px rgba(117,69,232,0.25) !important;
}

/* Streamlit buttons */
.stButton button {
    background: linear-gradient(110deg, #7545E8, #327CEB) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    transition: 0.25s ease !important;
}

.stButton button:hover {
    box-shadow: 0 0 22px rgba(117,69,232,0.4) !important;
    transform: translateY(-2px);
}

/* Glass containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.055) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(18px);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(10,15,35,0.96) !important;
    border-right: 1px solid rgba(167,139,250,0.2);
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(167,139,250,0.6) !important;
    border-radius: 18px !important;
    padding: 18px !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.15) !important;
}


/* BELVO - THEME ADAPTIVE BOX TEXT */

/* DARK MODE */
html[data-theme="dark"] .stTextInput input,
html[data-theme="dark"] .stTextArea textarea,
html[data-theme="dark"] .stNumberInput input,
html[data-theme="dark"] [data-testid="stFileUploader"] * {
    color: #FFFFFF !important;
}

/* LIGHT MODE */
html[data-theme="light"] .stTextInput input,
html[data-theme="light"] .stTextArea textarea,
html[data-theme="light"] .stNumberInput input,
html[data-theme="light"] [data-testid="stFileUploader"] * {
    color: #000000 !important;
}

/* PLACEHOLDER TEXT - DARK MODE */
html[data-theme="dark"] .stTextInput input::placeholder,
html[data-theme="dark"] .stTextArea textarea::placeholder {
    color: #D0D0D0 !important;
    opacity: 1 !important;
}

/* PLACEHOLDER TEXT - LIGHT MODE */
html[data-theme="light"] .stTextInput input::placeholder,
html[data-theme="light"] .stTextArea textarea::placeholder {
    color: #555555 !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)



# ------------ BELVO MEETING INTRO ANIMATION ------------

st.markdown("""
<style>
.belvo-intro {
    position: fixed;
    inset: 0;
    z-index: 999999;
    background: radial-gradient(circle at center, #19264b 0%, #080D1A 75%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: introExit 4.5s ease forwards;
    pointer-events: none;
}

.meeting-circle {
    width: 145px;
    height: 145px;
    border: 2px solid rgba(34,211,238,.7);
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    box-shadow: 0 0 35px rgba(34,211,238,.25);
    animation: pulse 1.5s infinite;
}

.meeting-circle::before,
.meeting-circle::after {
    content: "";
    position: absolute;
    inset: -15px;
    border: 1px solid rgba(139,92,246,.6);
    border-radius: 50%;
    animation: ripple 2s infinite;
}

.meeting-circle::after {
    animation-delay: 1s;
}

.mic { font-size: 55px; }

.wave {
    display: flex;
    align-items: center;
    gap: 5px;
    height: 55px;
    margin-top: 30px;
}

.wave span {
    width: 5px;
    height: 15px;
    border-radius: 8px;
    background: #22D3EE;
    animation: sound .7s infinite alternate;
}

.wave span:nth-child(even) {
    background: #A78BFA;
    animation-delay: .3s;
}

.belvo-name {
    margin-top: 25px;
    color: #FFFFFF !important;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 6px;
}

.belvo-tag {
    color: #22D3EE !important;
    font-size: 12px;
    letter-spacing: 3px;
    margin-top: 10px;
}

.belvo-features {
    display: flex;
    gap: 12px;
    margin-top: 30px;
    color: #C4B5FD !important;
    font-size: 10px;
    letter-spacing: 1px;
}

.belvo-features span {
    border: 1px solid rgba(167,139,250,.4);
    background: rgba(139,92,246,.12);
    padding: 8px 12px;
    border-radius: 20px;
}

@keyframes sound {
    to { height: 48px; }
}

@keyframes pulse {
    50% { transform: scale(1.07); }
}

@keyframes ripple {
    to { transform: scale(1.5); opacity: 0; }
}

@keyframes introExit {
    0%, 78% { opacity: 1; visibility: visible; }
    100% { opacity: 0; visibility: hidden; }
}
</style>

<div class="belvo-intro">
    
<div class="belvo-intro">
<div class="meeting-circle">
<div class="mic">🎙️</div>
</div>
<div class="wave">
<span></span><span></span><span></span><span></span>
<span></span><span></span><span></span><span></span>
<span></span><span></span><span></span><span></span>
</div>
<div class="belvo-name">BELVO MINUTES</div>
<div class="belvo-tag">TURN CONVERSATIONS INTO ACTION</div>
<div class="belvo-features">
<span>TRANSCRIPT</span>
<span>DECISIONS</span>
<span>ACTION ITEMS</span>
</div>
</div>

""", unsafe_allow_html=True)
