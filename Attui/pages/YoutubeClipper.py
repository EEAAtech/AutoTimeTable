import streamlit as st
import subprocess

st.set_page_config(page_title="YouTube Audio Clipper", layout="wide")

def main():
    st.title("YouTube Audio Clipper")
    st.markdown("Enter a YouTube URL and select start/end times to download an audio clip as MP3.")

    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("Start Time", placeholder="0:31", help="Format: MM:SS or HH:MM:SS")
    with col2:
        end_time = st.text_input("End Time", placeholder="0:45", help="Format: MM:SS or HH:MM:SS")

    if st.button("Download Audio Clip", type="primary"):
        if not url.strip():
            st.error("Please enter a YouTube URL.")
            return
        if not start_time.strip() or not end_time.strip():
            st.error("Please enter both start and end times.")
            return

        # Construct the download-sections parameter
        section = f"*{start_time}-{end_time}"
        command = f'yt-dlp --download-sections "{section}" -x --audio-format mp3 "{url}"'

        with st.spinner("Downloading audio clip..."):
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)  # 5 min timeout
                if result.returncode == 0:
                    st.success("✅ Audio clip downloaded successfully!")
                    if result.stdout.strip():
                        st.info(f"Output:\n{result.stdout}")
                else:
                    st.error("❌ Download failed.")
                    if result.stderr.strip():
                        st.error(f"Error details:\n{result.stderr}")
            except subprocess.TimeoutExpired:
                st.error("⏱️ Download timed out after 5 minutes.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()