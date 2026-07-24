import os
import tempfile
import streamlit as st
import whisper
from docx import Document

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Audio Translator",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Spanish Audio → English Word")
st.write("Upload a WAV, MP3 or M4A file and download the English transcript.")

# ==========================================================
# LOAD MODEL (Cached)
# ==========================================================

@st.cache_resource
def load_whisper_model(model_name):
    return whisper.load_model(model_name)

# ==========================================================
# MODEL SELECTION
# ==========================================================

MODEL_NAME = st.selectbox(
    "Select Whisper Model",
    ["tiny", "base", "small"],
    index=1
)

# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Audio",
    type=["wav", "mp3", "m4a"]
)

# ==========================================================
# MAIN
# ==========================================================

if uploaded_file is not None:

    if st.button("Convert to Word"):

        temp_audio_path = None
        output_path = None

        try:

            # Load model
            with st.spinner("Loading Whisper model..."):
                model = load_whisper_model(MODEL_NAME)

            # Save uploaded audio
            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_audio:
                tmp_audio.write(uploaded_file.read())
                temp_audio_path = tmp_audio.name

            st.info("Transcribing and translating...")

            # Transcribe
            result = model.transcribe(
                temp_audio_path,
                task="translate",
                language="es",
                fp16=False
            )

            # Create Word document
            doc = Document()
            doc.add_heading("Meeting Transcript", level=1)
            doc.add_paragraph(result["text"])

            output_path = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".docx"
            ).name

            doc.save(output_path)

            st.success("✅ Completed Successfully!")

            with open(output_path, "rb") as file:

                st.download_button(
                    label="📥 Download Word File",
                    data=file,
                    file_name="Meeting_Transcript.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")

        finally:

            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

            if output_path and os.path.exists(output_path):
                os.remove(output_path)
