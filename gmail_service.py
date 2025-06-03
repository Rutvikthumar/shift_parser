import base64
from googleapiclient.discovery import build

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def get_shift_emails(creds):
    service = get_gmail_service(creds)
    results = service.users().messages().list(
        userId='me',
        q='"TAL Pharmacy Recruitment Inc. Shifts"'
    ).execute()
    messages = results.get('messages', [])
    output = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        for part in msg_detail['payload'].get('parts', []):
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    output.append({'id': msg['id'], 'body': body})
                    break
        else:
            output.append({'id': msg['id'], 'body': msg_detail.get('snippet', '')})
    return output
