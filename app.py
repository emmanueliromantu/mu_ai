import streamlit as st
import subprocess
from pathlib import Path
import os
import time

st.set_page_config(page_title="Mu_AI", page_icon="🎵")

# SESSION MEMORY
if "done" not in st.session_state:
    st.session_state.done = False

if "files" not in st.session_state:
    st.session_state.files = []

st.title("🎵 Mu_AI - AI Music Splitter Pro")
st.write("Upload a song, listen, and split into vocals + instrumental.")

# Upload
uploaded_file = st.file_uploader("Upload your song (mp3 or wav)", type=["mp3", "wav"])

if uploaded_file is not None:

    input_dir = Path("input")
    output_dir = Path("output")

    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    file_path = input_dir / uploaded_file.name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully!")

    # 🎧 PLAY ORIGINAL
    st.subheader("🎧 Preview Original Song")
    st.audio(file_path)

    if st.button("🚀 Start Separation"):
        st.session_state.done = False
        st.session_state.files = []

        st.warning("⚠️ Use small songs (under 10MB)")
        st.info("Processing... please wait ⏳")

        # PROGRESS BAR
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Start process
        process = subprocess.Popen(
            [
                "python", "-m", "demucs",
                "-n", "htdemucs",
                "--two-stems=vocals",
                "--mp3",
                "-o", str(output_dir),
                str(file_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        progress = 0

        # FAKE SMOOTH PROGRESS
        while process.poll() is None:
            if progress < 95:
                progress += 1
                progress_bar.progress(progress)
                status_text.text(f"Processing... {progress}%")
                time.sleep(0.3)

        progress_bar.progress(100)
        status_text.text("Finalizing... 100%")

        # FIND OUTPUT
        model_folder = output_dir / "htdemucs"

        if model_folder.exists():
            latest = max(model_folder.iterdir(), key=os.path.getctime)
            files = list(latest.glob("*"))

            st.session_state.files = files
            st.session_state.done = True

            st.success("Separation complete 🎉")
        else:
            st.error("Something went wrong.")

# 🎧 RESULTS
if st.session_state.done:

    st.subheader("🎧 Listen & Download Your Splits")

    for f in st.session_state.files:

        st.write(f"### {f.name}")

        with open(f, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)

        with open(f, "rb") as file:
            st.download_button(
                label=f"⬇️ Download {f.name}",
                data=file,
                file_name=f.name
            )
