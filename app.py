
import streamlit as st
import os
from datetime import datetime
from audio_processing import process_audio
from transcription import transcribe_audio
from summarization import summarize_meeting
from decision_extraction import extract_decisions
from action_items import extract_action_items
from pdf_report import generate_meeting_pdf


# Application configuration
st.set_page_config(
    page_title="BELVO MINUTES",
    page_icon="🎙️",
    layout="wide"
)

# Create required folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed_audio", exist_ok=True)

# Application header
st.title("🎙️ BELVO MINUTES")
st.subheader("AI-Powered Meeting Intelligence Platform")

st.write(
    "Upload your meeting recording to generate "
    "transcripts, summaries, decisions and action items."
)

st.divider()

# Meeting upload section
st.header("📁 Upload Meeting Recording")

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
                "action_items": action_items
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
            action_items=report_data["action_items"]
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

/* Main background */
.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, #352064 0%, transparent 40%),
        radial-gradient(ellipse at 90% 80%, #103D60 0%, transparent 40%),
        #080D1A;
    color: #FFFFFF;
}

/* Main content */
[data-testid="stMain"] {
    background: transparent;
}

/* Sidebar glass */
[data-testid="stSidebar"] {
    background: rgba(18, 23, 48, 0.75) !important;
    backdrop-filter: blur(25px);
    border-right: 1px solid rgba(255,255,255,0.15);
}

/* Glass statistics cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.09) !important;
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}

/* Metric text */
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

/* Glass containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.055);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
}

/* Upload section */
[data-testid="stFileUploader"] {
    background: rgba(125, 90, 220, 0.12);
    backdrop-filter: blur(20px);
    border: 1px dashed #9B83FF;
    border-radius: 20px;
    padding: 22px;
}

/* Headings */
h1, h2, h3 {
    color: #FFFFFF !important;
    text-align: center;
}

/* Inputs */
.stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px;
    text-align: center;
}

/* Buttons */
.stButton button {
    background: linear-gradient(110deg, #7545E8, #327CEB) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    text-align: center;
    transition: 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(117,69,232,0.45);
}

/* Dividers */
hr {
    border-color: rgba(255,255,255,0.15);
}

/* Smooth appearance */
* {
    transition: border-color 0.25s ease;
}

</style>
""", unsafe_allow_html=True)



# ---------------- BELVO LOADING ANIMATION ----------------
if "belvo_intro_shown" not in st.session_state:
    st.session_state.belvo_intro_shown = True

    st.markdown("""
    <style>
    .belvo-splash {
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: radial-gradient(circle, #25204d, #080D1A 75%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        animation: belvoFade 3s ease forwards;
        pointer-events: none;
    }

    .belvo-logo {
        color: white;
        font-size: 42px;
        font-weight: 800;
        letter-spacing: 5px;
        animation: belvoGlow 1.5s infinite alternate;
    }

    .belvo-tagline {
        color: #9C9AFF;
        font-size: 14px;
        letter-spacing: 4px;
        margin-top: 12px;
        text-align: center;
    }

    .belvo-wave {
        display: flex;
        gap: 7px;
        margin-bottom: 30px;
        align-items: center;
        text-align: center;
    }

    .belvo-wave span {
        width: 5px;
        height: 25px;
        border-radius: 10px;
        background: #8B5CF6;
        animation: wave 0.8s infinite alternate;
        text-align: center;
    }

    .belvo-wave span:nth-child(2n) {
        animation-delay: 0.2s;
        background: #22D3EE;
    }

    .belvo-wave span:nth-child(3n) {
        animation-delay: 0.4s;
    }

    @keyframes wave {
        to { height: 65px; }
    }

    @keyframes belvoGlow {
        to { text-shadow: 0 0 25px #8B5CF6; }
    }

    @keyframes belvoFade {
        0%, 75% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; }
    }
    </style>

    <div class="belvo-splash">
        <div class="belvo-wave">
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
        </div>
        <div class="belvo-logo">BELVO MINUTES</div>
        <div class="belvo-tagline">TURN CONVERSATIONS INTO ACTION</div>
    </div>
    """, unsafe_allow_html=True)


# ------------ BELVO MEETING INTRO ANIMATION ------------
if "belvo_intro_shown" not in st.session_state:
    st.session_state.belvo_intro_shown = True

    st.markdown("""
    <style>
    .belvo-intro {
        position: fixed;
        inset: 0;
        z-index: 999999;
        background: radial-gradient(circle at center,
            #19264b 0%, #080D1A 70%);
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

    .mic {
        font-size: 55px;
        animation: micReveal 1.2s ease both;
    }

    .wave {
        display: flex;
        align-items: center;
        gap: 5px;
        height: 55px;
        margin-top: 35px;
    }

    .wave span {
        width: 5px;
        height: 15px;
        border-radius: 8px;
        background: #22D3EE;
        animation: sound 0.7s infinite alternate;
    }

    .wave span:nth-child(even) {
        background: #A78BFA;
        animation-delay: .3s;
    }

    .wave span:nth-child(3n) {
        animation-delay: .5s;
    }

    .belvo-name {
        margin-top: 25px;
        color: white;
        font-size: 38px;
        font-weight: 800;
        letter-spacing: 6px;
        animation: textReveal 1.5s ease both;
    }

    .belvo-tag {
        color: #22D3EE;
        font-size: 12px;
        letter-spacing: 3px;
        margin-top: 10px;
        animation: textReveal 2s ease both;
    }

    .belvo-features {
        display: flex;
        gap: 12px;
        margin-top: 30px;
        color: #C4B5FD;
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

    @keyframes micReveal {
        from { opacity: 0; transform: scale(.4); }
        to { opacity: 1; transform: scale(1); }
    }

    @keyframes textReveal {
        from { opacity: 0; transform: translateY(18px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes introExit {
        0%, 78% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; }
    }
    </style>

    <div class="belvo-intro">
        <div class="meeting-circle">
            <div class="mic">🎙️</div>
        </div>

        <div class="wave">
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
        </div>

        <div class="belvo-name">BELVO MINUTES</div>
        <div class="belvo-tag">
            TURN CONVERSATIONS INTO ACTION
        </div>

        <div class="belvo-features">
            <span>TRANSCRIPT</span>
            <span>DECISIONS</span>
            <span>ACTION ITEMS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

