import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
import datetime
import re

# Configuration -  IMPORTANT: Replace these with your actual details or use environment variables/Streamlit secrets
# It is highly recommended to use st.secrets for the PAT in production
GITHUB_PAT = os.environ.get("GITHUB_PAT") or st.secrets.get("GITHUB_PAT")
REPO_NAME = os.environ.get("GITHUB_REPO") or st.secrets.get("GITHUB_REPO") # Format: "username/repo-name"
JOURNALS_FOLDER = "journals"

TAGS = [
    "#$Physical/Cardio",
    "#$Physical/Bodio",
    "#$Mental/Read",
    "#$Rails",
    "#$Home",
    "#$Mental/Study",
    "#$Finance",
    "#$Music",
    "#$Modx",
    "#$Logic"
]

@st.cache_resource
def get_github_client():
    """Initializes and returns the PyGithub client."""
    if not GITHUB_PAT:
        st.error("GitHub PAT not found. Please set the GITHUB_PAT environment variable or add it to Streamlit secrets.")
        st.stop()
    return Github(GITHUB_PAT)

def get_file_path(selected_date):
    """Constructs the file path based on the selected date."""
    filename = f"{selected_date.strftime('%Y_%m_%d')}.md"
    return f"{JOURNALS_FOLDER}/{filename}"

def load_data_from_github(repo, file_path):
    """Loads content from the specified markdown file in the repo."""
    data = {tag: "" for tag in TAGS}
    file_content = ""
    sha = None
    
    try:
        file = repo.get_contents(file_path)
        file_content = file.decoded_content.decode('utf-8')
        sha = file.sha
        
        lines = file_content.splitlines()
        for line in lines:
            if "#$EodLog" in line:
                for tag in TAGS:
                    if tag in line:
                        # Extract the text after the tag and #$EodLog, or the whole line depending on format
                        # Here we load the entire line for the user to edit
                        data[tag] = line
                        break # Assume one tag per line based on description
                        
    except UnknownObjectException:
        st.warning(f"File {file_path} not found in the repository. A new one will be created upon saving.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

    return data, file_content, sha

def ensure_bullet_prefix(text):
    """Ensures the string starts with '- ' if it isn't already."""
    text = text.strip()
    if not text:
        return ""
    if text.startswith("- "):
        return text
    return f"- {text}"

def save_data_to_github(repo, file_path, original_content, file_sha, current_inputs, selected_date):
    """Updates or creates the markdown file with new text box values."""
    new_lines = []
    
    if original_content:
        lines = original_content.splitlines()
        # Create a copy of current_inputs to track which ones we've updated
        pending_updates = dict(current_inputs)
        
        for line in lines:
            line_updated = False
            if "#$EodLog" in line:
                for tag in TAGS:
                    if tag in line:
                        # Replace the line with the new input if it exists
                        new_val = pending_updates.get(tag, "").strip()
                        if new_val:
                            # Apply prefix to existing line update
                            new_lines.append(ensure_bullet_prefix(new_val))
                            del pending_updates[tag] # Mark as processed
                        else:
                            # If input is empty, maybe keep original or remove? 
                            # Sticking to "replace by values of text box", if empty, it becomes empty string (effectively removing it if we don't append)
                            # Let's append the empty string or skip if we want to delete. Let's just update to empty if user cleared it.
                            new_lines.append("") 
                            if tag in pending_updates:
                                del pending_updates[tag]
                        line_updated = True
                        break # Moved to next line in original file
                        
            if not line_updated:
                new_lines.append(line)
                
        for tag, val in pending_updates.items():
            if val.strip():
                # If the user typed something but the tag wasn't in the file before, append it
                # We need to ensure it has #$EodLog and the tag if the user didn't type it
                formatted_val = val.strip()
                if "#$EodLog" not in formatted_val:
                    formatted_val = f"{formatted_val} #$EodLog"
                if tag not in formatted_val:
                    formatted_val = f"{formatted_val} {tag}"
                # Apply prefix to new appended line
                new_lines.append(ensure_bullet_prefix(formatted_val))
                
        updated_content = "\n".join(new_lines)
    else:
        for tag, val in current_inputs.items():
            if val.strip():
                formatted_val = val.strip()
                if "#$EodLog" not in formatted_val:
                    formatted_val = f"{formatted_val} #$EodLog"
                if tag not in formatted_val:
                    formatted_val = f"{formatted_val} {tag}"
                # Apply prefix to new file content
                new_lines.append(ensure_bullet_prefix(formatted_val))
        updated_content = "\n".join(new_lines)

    commit_message = f"Eod log for {selected_date.strftime('%Y-%m-%d')}"
    
    try:
        if file_sha:
            repo.update_file(file_path, commit_message, updated_content, file_sha)
            st.success(f"Successfully updated {file_path}")
        else:
            # If no sha, file didn't exist, create it
            repo.create_file(file_path, commit_message, updated_content)
            st.success(f"Successfully created {file_path}")
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")

def main():
    st.set_page_config(page_title="EOD Log App", layout="centered")
    st.title("EOD Log Entry")

    # Ensure required configuration is present
    if not REPO_NAME:
         st.error("GitHub Repository name not configured. Set GITHUB_REPO environment variable or secret.")
         st.stop()

    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Date picker defaulting to today
        selected_date = st.date_input("Select Date", datetime.date.today())
        
    gh = get_github_client()
    try:
        repo = gh.get_repo(REPO_NAME)
    except Exception as e:
        st.error(f"Could not access repository {REPO_NAME}. Check your PAT and repo name. Error: {e}")
        st.stop()

    file_path = get_file_path(selected_date)
    
    # Use session state to hold data across re-runs when interacting with inputs
    # If date changes, we need to reload
    if 'current_date' not in st.session_state or st.session_state.current_date != selected_date:
        with st.spinner(f"Loading data for {selected_date}..."):
            data, original_content, file_sha = load_data_from_github(repo, file_path)
            st.session_state.data = data
            st.session_state.original_content = original_content
            st.session_state.file_sha = file_sha
            st.session_state.current_date = selected_date
            
    # Dictionary to hold the current values of the text areas
    current_inputs = {}

    st.write("---")
    for tag in TAGS:
        # We pre-fill the text area with the line found from the markdown
        current_inputs[tag] = st.text_area(
            label=tag,
            value=st.session_state.data.get(tag, ""),
            height=100, # Approximate height for 3 lines
            key=f"input_{tag}"
        )

    with col2:
        # Align button with date picker somewhat
        st.write("") 
        st.write("")
        if st.button("Save", type="primary", use_container_width=True):
            with st.spinner("Saving to GitHub..."):
                save_data_to_github(
                    repo, 
                    file_path, 
                    st.session_state.original_content, 
                    st.session_state.file_sha, 
                    current_inputs, 
                    selected_date
                )
                # Refresh data after save to get new SHA
                data, original_content, file_sha = load_data_from_github(repo, file_path)
                st.session_state.data = data
                st.session_state.original_content = original_content
                st.session_state.file_sha = file_sha
                
if __name__ == "__main__":
    main()