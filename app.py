import streamlit as st
import pandas as pd
from gmail_parser import parse_gmail_shifts
from drive_parser import parse_drive_shifts
from cache_manager import load_cache, update_cache
from sheets_export import export_to_csv
import os

st.set_page_config(page_title="TAL Pharmacy Shift Parser", layout="wide")
st.title("TAL Pharmacy Shift Parser")
st.markdown("One-click tool for parsing Gmail and WhatsApp shift data.")

if st.button("Parse Now"):
    cache = load_cache()
    gmail_shifts, gmail_ids = parse_gmail_shifts(cache["gmail_ids"])
    drive_shifts, drive_ids = parse_drive_shifts(cache["drive_ids"])
    all_shifts = gmail_shifts + drive_shifts

    # Deduplicate and update cache
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
    if os.path.exists("output/shifts.csv"):
        with open("output/shifts.csv", "rb") as f:
            st.download_button("Download last CSV", f, "shifts.csv")