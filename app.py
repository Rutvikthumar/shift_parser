import streamlit as st
import pandas as pd
from gmail_parser import parse_gmail_shifts
from drive_parser import parse_drive_shifts
from cache_manager import load_cache, update_cache
from sheets_export import export_to_csv, export_to_gsheet

st.set_page_config(page_title="Shift Parser", layout="wide")
st.title("TAL Pharmacy Shift Parser")

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
        export_to_gsheet(df)
    else:
        st.info("No new shift data found.")
