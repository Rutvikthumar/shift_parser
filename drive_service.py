import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import io
import zipfile

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Set this to your target Drive folder name or ID
FOLDER_NAME = "whatsapp_shifts"

def get_drive_service():
    creds = None
    if os.path.exists('token_drive.json'):
        creds = Credentials.from_authorized_user_file('token_drive.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_drive.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_drive.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def get_whatsapp_txts():
    service = get_drive_service()
    # Find folder
    results = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name='{FOLDER_NAME}'",
                                   spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    if not folders:
        return []
    folder_id = folders[0]['id']

    # List all .zip and .txt in folder
    results = service.files().list(
        q=f"'{folder_id}' in parents and (name contains '.zip' or name contains '.txt')",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    txts = []

    for file in files:
        request = service.files().get_media(fileId=file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        if file['name'].endswith('.zip'):
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
                if name.endswith('.txt'):
                    txts.append({'id': file['id'] + ':' + name, 'content': z.read(name).decode('utf-8')})
        elif file['name'].endswith('.txt'):
            txts.append({'id': file['id'], 'content': fh.read().decode('utf-8')})
    return txts