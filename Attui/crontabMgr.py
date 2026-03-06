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

# Function to extract and execute command from crontab line
def execute_cron_line(line):
    # Find the first occurrence of "/home"
    start_idx = line.find("/home")
    if start_idx == -1:
        st.error("No executable path found in this line (must contain '/home')")
        return
    
    # Extract the command (everything from "/home" onwards)
    command = line[start_idx:]
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            st.success(f"✅ Executed: {command}")
            if result.stdout:
                st.info(f"Output: {result.stdout}")
        else:
            st.error(f"❌ Command failed with exit code {result.returncode}")
            if result.stderr:
                st.error(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        st.error(f"⏱️ Command timed out after 10 seconds")
    except Exception as e:
        st.error(f"❌ Error executing command: {str(e)}")

# Streamlit app
def main():
    st.title("Crontab Entry Manager")
    
    lines = st.session_state.crontab_content
    
    # Display each crontab line with a checkbox and execution button
    st.subheader("Crontab Entries")
    
    for i, line in enumerate(lines):
        if not line.strip():  # Skip empty lines
            continue
            
        # lines prefixed with '#' are considered disabled, so the checkbox should be off
        checked = not line.startswith("#")
        
        # Create columns: checkbox | button | line content
        col1, col2, col3 = st.columns([1, 1, 6])
        
        with col1:
            # use a stable key so Streamlit can track changes
            new_checked = st.checkbox("Enable", value=checked, key=f"chk_{i}", label_visibility="collapsed")
            # if the user flipped the checkbox, toggle only that line
            if new_checked != checked:
                toggle_cron(i)
        
        with col2:
            if st.button("⚡", key=f"exec_{i}", help="Execute this cron command"):
                execute_cron_line(st.session_state.crontab_content[i])
        
        with col3:
            st.text(f"{i}: {line}")
    
    # Add save button
    st.divider()
    if st.button("Save Changes to Crontab", type="primary"):
        save_crontab()

if __name__ == "__main__":
    main()
