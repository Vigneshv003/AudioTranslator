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

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

# ==========================================================
# LOAD MODEL (Only Once)
# ==========================================================

@st.cache_resource(show_spinner=False)
def load_model(model_name):
    return whisper.load_model(model_name)

# ==========================================================
# MODEL
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

if uploaded_file:

    # Limit upload size
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("❌ File size exceeds 25 MB.")
        st.stop()

    st.write(f"**File:** {uploaded_file.name}")
    st.write(f"**Size:** {uploaded_file.size/1024/1024:.2f} MB")

    if st.button("Convert to Word", type="primary"):

        temp_audio_path = None
        output_doc = None

        try:

            progress = st.progress(0)

            progress.progress(10)

            # Load Whisper Model
            with st.spinner("Loading Whisper Model..."):
                model = load_model(MODEL_NAME)

            progress.progress(30)

            # Save uploaded file
            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
                temp_audio.write(uploaded_file.getbuffer())
                temp_audio_path = temp_audio.name

            progress.progress(50)

            with st.spinner("Transcribing Audio..."):

                result = model.transcribe(
                    temp_audio_path,
                    task="translate",
                    language="es",
                    fp16=False
                )

            progress.progress(80)

            # Create Word document
            doc = Document()
            doc.add_heading("Meeting Transcript", level=1)
            doc.add_paragraph(result["text"])

            output_doc = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".docx"
            ).name

            doc.save(output_doc)

            progress.progress(100)

            st.success("✅ Translation Completed!")

            with open(output_doc, "rb") as f:

                st.download_button(
                    "📥 Download Word File",
                    data=f.read(),
                    file_name="Meeting_Transcript.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:

            st.error(f"❌ {e}")

        finally:

            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

            if output_doc and os.path.exists(output_doc):
                os.remove(output_doc)
