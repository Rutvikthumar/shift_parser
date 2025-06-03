import streamlit as st
import pandas as pd
import tempfile

from gmail_parser import parse_gmail_shifts
from drive_parser import parse_drive_shifts
from cache_manager import load_cache, update_cache
from sheets_export import export_to_csv

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

st.set_page_config(page_title="TAL Pharmacy Shift Parser", layout="wide")
st.title("TAL Pharmacy Shift Parser")
st.markdown("One-click tool for parsing Gmail and WhatsApp shift data.")

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
    creds = flow.run_console()
    st.session_state["google_creds"] = creds
else:
    creds = st.session_state["google_creds"]

st.success("✅ Authenticated with Google. Ready to parse shifts!")

if st.button("Parse Now"):
    cache = load_cache()
    gmail_shifts, gmail_ids = parse_gmail_shifts(cache["gmail_ids"], creds)
    drive_shifts, drive_ids = parse_drive_shifts(cache["drive_ids"], creds)
    all_shifts = gmail_shifts + drive_shifts

    update_cache(gmail_ids, drive_ids)
    if all_shifts:
        df = pd.DataFrame(all_shifts)
        st.dataframe(df)
        export_to_csv(df)
        st.success(f"Exported {len(all_shifts)} shifts to output/shifts.csv")
        with open("output/shifts.csv", "rb") as f:
            st.download_button("Download CSV", f, "shifts.csv")
    else:
        st.info("No new shift data found.")
else:
    try:
        with open("output/shifts.csv", "rb") as f:
            st.download_button("Download last CSV", f, "shifts.csv")
    except FileNotFoundError:
        pass
