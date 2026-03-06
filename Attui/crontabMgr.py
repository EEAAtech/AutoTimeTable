import os

import streamlit as st
import subprocess

st.set_page_config(layout="wide")

# Function to get current crontab content
def get_crontab():
    return subprocess.check_output("crontab -l", shell=True).decode()

# Initialize session state
if "crontab_content" not in st.session_state:
    st.session_state.crontab_content = get_crontab().splitlines()

# Function to modify a specific line in the crontab (in memory only)
def toggle_cron(line_number):
    if 0 <= line_number < len(st.session_state.crontab_content):
        line = st.session_state.crontab_content[line_number]
        # Toggle the "#" prefix
        if line.startswith("#"):
            st.session_state.crontab_content[line_number] = line[1:]
        else:
            st.session_state.crontab_content[line_number] = "#" + line
    else:
        st.error("Invalid line number.")

# Function to save crontab to disk
def save_crontab():
    with open("temp_crontab", "w") as f:
        for line in st.session_state.crontab_content:
            f.write(line + "\n")
    subprocess.run("crontab < temp_crontab", shell=True)
    st.success("Crontab updated successfully!")

# Streamlit app
def main():
    #st.set_option('server.port', 8502)  # Set server port to avoid conflict with default
    st.title("Crontab Entry Blocker")
    
    lines = st.session_state.crontab_content
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Crontab Entries","730Alarm", "Mass", "Tea", "Dinner","Rosary", "crontabMgr"])
    
    with tab1:
        # Display each crontab line with a checkbox; checked means enabled (not commented)
        for i, line in enumerate(lines):
            # lines prefixed with '#' are considered disabled, so the checkbox should be off
            checked = not line.startswith("#")
            # use a stable key so Streamlit can track changes
            new_checked = st.checkbox(f"{i}: = = = : {line}", value=checked, key=f"chk_{i}")
            # if the user flipped the checkbox, toggle only that line
            if new_checked != checked:
                toggle_cron(i)
        
        # Add save button
        st.divider()
        if st.button("Save Changes to Crontab", type="primary"):
            save_crontab()
    with tab2:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/730Alarm.log"):
            with open("/home/ea/AutoTimeTable/730Alarm.log", "r") as log_file:
                st.text(log_file.read())
    with tab3:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/Daily_Mass.log"):
            with open("/home/ea/AutoTimeTable/Daily_Mass.log", "r") as log_file:
                st.text(log_file.read())
    with tab4:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/Tea.log"):
            with open("/home/ea/AutoTimeTable/Tea.log", "r") as log_file:
                st.text(log_file.read())
    with tab5:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/Dinner.log"):
            with open("/home/ea/AutoTimeTable/Dinner.log", "r") as log_file:
                st.text(log_file.read())
    with tab6:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/Daily_Rosary.log"):
            with open("/home/ea/AutoTimeTable/Daily_Rosary.log", "r") as log_file:
                st.text(log_file.read())
    with tab7:
        # Display log files in tabs
        if os.path.exists("/home/ea/AutoTimeTable/Attui/crontabMgr.log"):
            with open("/home/ea/AutoTimeTable/Attui/crontabMgr.log", "r") as log_file:
                st.text(log_file.read())

if __name__ == "__main__":
    main()