import streamlit as st
import os
import subprocess
from pathlib import Path

st.set_page_config(page_title="Mu_AI", page_icon="🎵")

st.title("🎵 Mu_AI - AI Music Splitter Pro")
st.write("Upload a song and split it into vocals, drums, bass, and instrumentals using AI.")

# Upload
uploaded_file = st.file_uploader("Upload your song (mp3 or wav)", type=["mp3", "wav"])

mode = st.radio(
    "Choose split mode:",
    ["Full Separation (vocals, drums, bass, other)", "Vocals + Instrumental only"]
)

if uploaded_file is not None:

    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    file_path = input_dir / uploaded_file.name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully!")

    if st.button("🚀 Start Separation"):

        st.info("Processing... please wait ⏳ This may take a few minutes.")

        # COMMAND
        if mode == "Vocals + Instrumental only":
            command = [
                "python", "-m", "demucs",
                "-n", "htdemucs",
                "--two-stems=vocals",
                "--mp3",
                "-o", str(output_dir),
                str(file_path)
            ]
        else:
            command = [
                "python", "-m", "demucs",
                "-n", "htdemucs",
                "--mp3",
                "-o", str(output_dir),
                str(file_path)
            ]

        # RUN DEMUCS
        process = subprocess.run(command)

        st.success("Separation complete 🎉")

        # FIND OUTPUT
        model_folder = output_dir / "htdemucs"

        if not model_folder.exists():
            st.error("No output folder found. Something went wrong.")
        else:
            latest = max(model_folder.iterdir(), key=os.path.getctime)

            files = list(latest.glob("*"))

            if len(files) == 0:
                st.error("No audio files found.")
            else:
                st.subheader("🎧 Download your separated files")

                for f in files:
                    with open(f, "rb") as file:
                        st.download_button(
                            label=f"⬇️ Download {f.name}",
                            data=file,
                            file_name=f.name
                        )