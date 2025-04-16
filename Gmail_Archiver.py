from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Csak módosításhoz szükséges scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ITT használjuk a credentials.json-t!
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # token.json most keletkezik
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def archive_all_inbox_emails(service):
    user_id = 'me'
    query = 'label:inbox'

    print("📬 Lekérdezés: beérkező levelek...")
    messages = []
    response = service.users().messages().list(userId=user_id, q=query).execute()

    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        response = service.users().messages().list(userId=user_id, q=query, pageToken=response['nextPageToken']).execute()
        messages.extend(response['messages'])

    print(f"📦 Archiválandó levelek száma: {len(messages)}")

    for msg in messages:
        service.users().messages().modify(
            userId=user_id,
            id=msg['id'],
            body={'removeLabelIds': ['INBOX']}
        ).execute()

    print("✅ Minden beérkező levél archiválva.")

if __name__ == '__main__':
    service = gmail_authenticate()
    archive_all_inbox_emails(service)
