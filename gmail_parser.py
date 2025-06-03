from shift_extract import parse_shift_email
from gmail_service import get_shift_emails

def parse_gmail_shifts(processed_ids, creds):
    """
    Fetch and parse Gmail shift emails, skipping processed_ids.
    Returns: (list of shift dicts, list of new Gmail message IDs)
    """
    messages = get_shift_emails(creds)  # [{id, body}]
    new_shifts = []
    new_ids = []
    for msg in messages:
        if msg['id'] in processed_ids:
            continue
        shift_dicts = parse_shift_email(msg["body"])
        for sd in shift_dicts:
            sd["source"] = "gmail"
            sd["email_id"] = msg["id"]
        new_shifts.extend(shift_dicts)
        new_ids.append(msg["id"])
    return new_shifts, new_ids
