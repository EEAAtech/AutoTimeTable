import streamlit as st
import subprocess

st.set_page_config(page_title="Crontab Simple Editor", layout="wide")

# Helper: load current crontab
@st.cache_data(show_spinner=False)
def load_crontab():
    try:
        current = subprocess.check_output("crontab -l", shell=True, text=True, stderr=subprocess.STDOUT)
        return current
    except subprocess.CalledProcessError as e:
        # No crontab installed yields exit 1 and text like "no crontab for user"
        if e.returncode == 1:
            return ""
        raise
    except Exception as e:
        st.error(f"Failed to load crontab: {str(e)}")
        return ""

# Helper: save crontab from text
def save_crontab(content: str):
    try:
        result = subprocess.run("crontab -", shell=True, input=content, text=True, capture_output=True)
        if result.returncode == 0:
            st.success("Crontab updated successfully.")
            st.cache_data.clear()
        else:
            st.error(f"Failed to update crontab. Exit code {result.returncode}")
            if result.stderr:
                st.error(result.stderr)
    except Exception as e:
        st.error(f"Failed to save crontab: {str(e)}")


def main():
    st.title("Simple Crontab Editor")
    st.markdown("Edit your `crontab -l` content below and click Save to apply.")

    if "crontab_text" not in st.session_state:
        st.session_state.crontab_text = load_crontab()

    if st.button("Save Crontab", type="primary"):
        save_crontab(st.session_state.crontab_text)

    st.text_area("Crontab content", value=st.session_state.crontab_text, height=520, key="crontab_text", placeholder="Write crontab entries here...")


if __name__ == "__main__":
    main()