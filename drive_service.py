from whatsapp_shift_parser import parse_whatsapp_shifts
from drive_service import get_whatsapp_txts

def parse_drive_shifts(processed_ids, creds):
    """
    Fetch and parse WhatsApp chat TXT files from Drive (unzipped), skipping processed_ids.
    Returns: (list of shift dicts, list of new Drive file IDs)
    """
    txt_files = get_whatsapp_txts(creds)
    new_shifts = []
    new_ids = []
    for file in txt_files:
        if file['id'] in processed_ids:
            continue
        shift_dicts = parse_whatsapp_shifts(file["content"])
        for sd in shift_dicts:
            sd["source"] = "drive"
            sd["file_id"] = file["id"]
        new_shifts.extend(shift_dicts)
        new_ids.append(file["id"])
    return new_shifts, new_ids
