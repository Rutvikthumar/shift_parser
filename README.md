# TAL Pharmacy Shift Parser

**One-click app to extract shifts from Gmail and WhatsApp chats (Google Drive).**

## Features

- Gmail API: Fetch and parse shift emails
- Google Drive API: Parse WhatsApp `.txt` files from ZIPs or text
- Handles complex date/time ranges and multiple shifts per day
- Extracts location and system used
- Deduplication of processed emails/files
- Outputs to CSV (and can be extended to Google Sheets)
- Streamlit UI (mobile-friendly)

## Setup

1. Clone this repo
2. Install requirements:  
   `pip install -r requirements.txt`
3. Place your Google API credentials as `credentials.json` (Gmail) and `credentials_drive.json` (Drive)
4. Run:  
   `streamlit run app.py`
5. On first run, authenticate for Gmail and Drive in your browser as prompted.

Shifts will be exported to `output/shifts.csv`.