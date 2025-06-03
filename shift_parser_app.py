
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Shift Parser", layout="centered")

st.title("📅 TAL Pharmacy Shift Parser")
st.write("This app fetches shift data from Gmail and WhatsApp chat backups.")

if st.button("Parse Gmail"):
    st.info("Gmail parsing coming soon...")

if st.button("Parse WhatsApp"):
    st.info("WhatsApp parsing coming soon...")

st.write("Once parsed, shifts will be displayed below and can be exported as CSV.")
