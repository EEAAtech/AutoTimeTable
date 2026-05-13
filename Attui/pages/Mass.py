import os
import streamlit as st

st.set_page_config(layout="wide")
st.title("Daily Mass Log")

log_file = "/home/ea/AutoTimeTable/Daily_Mass.log"
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        st.text(f.read())
else:
    st.info("Log file not found")
