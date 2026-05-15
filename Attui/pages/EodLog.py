import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
import datetime
import re

# Configuration - IMPORTANT: Replace these with your actual details or use environment variables/Streamlit secrets
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
    "#$Logic",
    "#$Mental/Study/NapoleonHill15LawsOfSuccess",
    "#$TTM"
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
    data = {tag: {"text": "", "disrupt_tag": ""} for tag in TAGS}
    file_content = ""
    sha = None
    
    try:
        file = repo.get_contents(file_path)
        file_content = file.decoded_content.decode('utf-8')
        sha = file.sha
        
        lines = file_content.splitlines()
        for line in lines:
            if "#$EodLog" in line or "#$Disrupt" in line:
                # Check for the disruption pattern first: - [disrupt_tag] [contents] #$Disrupt -> [tag]
                disrupt_match = re.search(r'-\s*(#\$\S+)\s+(.*?)\s+#\$Disrupt\s*->\s*(#\$\S+)', line)
                if disrupt_match:
                    disrupt_tag = disrupt_match.group(1)
                    content = disrupt_match.group(2)
                    target_tag = disrupt_match.group(3)
                    if target_tag in data:
                        data[target_tag] = {"text": content, "disrupt_tag": disrupt_tag}
                        continue

                # Fallback to standard tag extraction if not a disruption line
                for tag in TAGS:
                    if tag in line:
                        # Strip standard formatting indicators to extract pure content
                        clean_content = line.replace("- ", "").replace(tag, "").replace("#$EodLog", "").strip()
                        data[tag] = {"text": clean_content, "disrupt_tag": ""}
                        break # Assume one target tag per line based on description
                        
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
            # Check if this line matches a target tag via disruption pattern or normal check
            matched_tag = None
            disrupt_match = re.search(r'-\s*(#\$\S+)\s+(.*?)\s+#\$Disrupt\s*->\s*(#\$\S+)', line)
            if disrupt_match:
                matched_tag = disrupt_match.group(3)
            else:
                for tag in TAGS:
                    if tag in line:
                        matched_tag = tag
                        break
            
            if matched_tag and matched_tag in pending_updates:
                input_data = pending_updates.get(matched_tag)
                val = input_data["text"].strip()
                disrupt_tag = input_data["disrupt_tag"]
                
                if val:
                    if disrupt_tag:
                        formatted_val = f"{disrupt_tag} {val} #$Disrupt -> {matched_tag}"
                    else:
                        formatted_val = f"{val} #$EodLog {matched_tag}"
                    new_lines.append(ensure_bullet_prefix(formatted_val))
                else:
                    new_lines.append("") 
                
                del pending_updates[matched_tag]
                line_updated = True
                        
            if not line_updated:
                new_lines.append(line)
                
        for tag, input_data in pending_updates.items():
            val = input_data["text"].strip()
            disrupt_tag = input_data["disrupt_tag"]
            if val:
                if disrupt_tag:
                    formatted_val = f"{disrupt_tag} {val} #$Disrupt -> {tag}"
                else:
                    formatted_val = f"{val} #$EodLog {tag}"
                new_lines.append(ensure_bullet_prefix(formatted_val))
                
        updated_content = "\n".join(new_lines)
    else:
        for tag, input_data in current_inputs.items():
            val = input_data["text"].strip()
            disrupt_tag = input_data["disrupt_tag"]
            if val:
                if disrupt_tag:
                    formatted_val = f"{disrupt_tag} {val} #$Disrupt -> {tag}"
                else:
                    formatted_val = f"{val} #$EodLog {tag}"
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
            
    # Dictionary to hold the current values of the text areas and dropdowns
    current_inputs = {}

    st.write("---")
    for tag in TAGS:
        # Fetch loaded values safely
        loaded_info = st.session_state.data.get(tag, {"text": "", "disrupt_tag": ""})
        loaded_text = loaded_info["text"]
        loaded_disrupt = loaded_info["disrupt_tag"]

        # Form dynamic columns for label alignment and the dropdown layout
        lbl_col, drop_col = st.columns([2, 3])
        with lbl_col:
            st.markdown(f"**{tag}**")
        with drop_col:
            dropdown_options = [""] + TAGS
            default_index = dropdown_options.index(loaded_disrupt) if loaded_disrupt in dropdown_options else 0
            selected_dropdown = st.selectbox(
                "Disrupted by:",
                options=dropdown_options,
                index=default_index,
                key=f"drop_{tag}",
                label_visibility="collapsed"
            )

        # Content Text Box
        ui_text_content = st.text_area(
            label=tag,
            value=loaded_text,
            height=100, # Approximate height for 3 lines
            key=f"input_{tag}",
            label_visibility="collapsed"
        )
        
        current_inputs[tag] = {
            "text": ui_text_content,
            "disrupt_tag": selected_dropdown
        }
        st.write("")

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