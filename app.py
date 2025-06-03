import streamlit as st
import tempfile
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

uploaded_creds = st.file_uploader(
    "Upload your Google OAuth credentials.json (never share this file!)",
    type="json"
)
if uploaded_creds is None:
    st.info("Please upload your credentials.json to use the app.")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
    tf.write(uploaded_creds.read())
    creds_path = tf.name

if "google_creds" not in st.session_state:
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.info("**Step 1:** Click the link below to authenticate with Google.\n\n**Step 2:** Approve and copy the code you are given.")
    st.markdown(f"[Authenticate with Google]({auth_url})")
    auth_code = st.text_input("Paste here the code you get after authenticating:")

    if auth_code:
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            st.session_state["google_creds"] = creds
            st.success("✅ Successfully authenticated!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.stop()
    else:
        st.stop()
else:
    creds = st.session_state["google_creds"]
