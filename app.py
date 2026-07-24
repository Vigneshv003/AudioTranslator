import os
import tempfile
import shutil
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
# FFMPEG PATH (Only needed on your local machine)
# Remove this after deployment if FFmpeg is installed normally
# ==========================================================


    

# ==========================================================
# MODEL
# ==========================================================

MODEL_NAME = st.selectbox(
    "Select Whisper Model",
    ["small", "medium", "large-v3"],
    index=0
)

uploaded_file = st.file_uploader(
    "Upload Audio",
    type=["wav", "mp3", "m4a"]
)

if uploaded_file:

    if st.button("Convert to Word"):

        with st.spinner("Loading Whisper model..."):

            model = whisper.load_model(MODEL_NAME)

        # Save uploaded file temporarily
        suffix = os.path.splitext(uploaded_file.name)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_audio:
            tmp_audio.write(uploaded_file.read())
            temp_audio_path = tmp_audio.name

        st.info("Transcribing and translating...")

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

        os.remove(temp_audio_path)

        st.success("Completed Successfully!")

        with open(output_path, "rb") as file:

            st.download_button(
                label="📥 Download Word File",
                data=file,
                file_name="Meeting_Transcript.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        os.remove(output_path)
