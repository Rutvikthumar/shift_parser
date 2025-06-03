import streamlit as st
import tempfile
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]
REDIRECT_URI = "https://shiftparser-gdxmz98re9g3npkaxgskke.streamlit.app/"

st.title("Shift Parser with Seamless Google OAuth")

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

def authenticate():
    flow = Flow.from_client_secrets_file(
        creds_path,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        include_granted_scopes='true'
    )
    st.info("**Step 1:** Click the link to authenticate with Google.\
             \n**Step 2:** Approve and copy the **full URL** from your browser after authenticating.")
    st.markdown(f"[Authenticate with Google]({auth_url})")
    auth_response = st.text_input("Paste the **full URL** you were redirected to after login:")
    if auth_response:
        try:
            flow.fetch_token(authorization_response=auth_response)
            creds = flow.credentials
            st.session_state["google_creds"] = creds
            st.session_state["just_authenticated"] = True
            st.success("✅ Successfully authenticated!")
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.stop()
    else:
        st.stop()

def run_shift_parser(creds):
    st.header("Shift Parser Main App")
    st.success("You are authenticated! Add your main logic here.")
    # Example logic: list user's Gmail labels (replace with your own)
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        st.write('No labels found.')
    else:
        st.write('Labels:')
        for label in labels:
            st.write(f"- {label['name']}")

if "google_creds" not in st.session_state:
    authenticate()
else:
    creds = st.session_state["google_creds"]
    if st.session_state.pop("just_authenticated", False):
        st.balloons()
        st.success("Welcome! You just authenticated.")
        run_shift_parser(creds)
    else:
        run_shift_parser(creds)
