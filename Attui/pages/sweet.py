import streamlit as st

html_file_path = "static/SweetsDB.htm" # Adjust to your actual HTML filename

try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Inject the correct static path directly into a global JS variable inside the HTML
    excel_route = "/app/static/SweetsDB.xlsx"
    injected_script = f"<script>const INJECTED_EXCEL_URL = '{excel_route}';</script>"
    html_content = html_content.replace("<head>", f"<head>\n{injected_script}")
    
    st.html(html_content)
    
except FileNotFoundError:
    st.error(f"Could not find HTML file at {html_file_path}")