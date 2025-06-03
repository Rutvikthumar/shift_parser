# TAL Pharmacy Shift Parser

**One-click app to extract shifts from Gmail and WhatsApp chats (Google Drive).**

## Features

- Gmail API: Fetch and parse shift emails
- Google Drive API: Parse WhatsApp `.txt` files from ZIPs
- Handles complex date/time ranges and multiple shifts per day
- Extracts location and system used
- Deduplication of processed emails/files
- Outputs to Google Sheets or CSV
- Streamlit UI (mobile-friendly)

## Setup

1. Clone this repo
2. Install requirements:  
   `pip install -r requirements.txt`
3. Add your Google API credentials (see docs)
4. Run:  
   `streamlit run app.py`