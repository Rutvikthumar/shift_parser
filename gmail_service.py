import os
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these SCOPES, delete the token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_shift_emails():
    service = get_gmail_service()
    # Search for emails with subject
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
            # fallback: try snippet
            output.append({'id': msg['id'], 'body': msg_detail.get('snippet', '')})
    return output