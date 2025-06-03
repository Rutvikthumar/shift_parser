import streamlit as st
import tempfile
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

uploaded_creds = st.file_uploader(
    "Upload your Google OAuth credentials.json (from Web client!)",
    type="json"
)
if uploaded_creds is None:
    st.info("Please upload your credentials.json to use the app.")
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
    tf.write(uploaded_creds.read())
    creds_path = tf.name

REDIRECT_URI = "https://shiftparser-gdxmz98re9g3npkaxgskke.streamlit.app/"

if "google_creds" not in st.session_state:
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Step 1: Create authorization URL
    auth_url, state = flow.authorization_url(prompt='consent', include_granted_scopes='true')

    st.info("**Step 1:** Click the link below to authenticate with Google.\n\n**Step 2:** Approve, and after you are redirected, copy the full URL from your browser's address bar and paste it below.")
    st.markdown(f"[Authenticate with Google]({auth_url})")
    auth_response = st.text_input("Paste the **full URL** you were redirected to after Google login:")

    if auth_response:
        try:
            flow.fetch_token(authorization_response=auth_response)
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
