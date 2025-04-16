from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def gmail_authenticate():
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

def archive_filtered_emails(
    service,
    exclude_starred=True,
    exclude_important=True,
    only_read=True,
    before_date=None,
    after_date=None
):
    user_id = 'me'
    query_parts = ['label:inbox']

    if exclude_starred:
        query_parts.append('-is:starred')
    if exclude_important:
        query_parts.append('-label:important')
    if only_read:
        query_parts.append('is:read')
    if before_date:
        query_parts.append(f"before:{before_date}")
    if after_date:
        query_parts.append(f"after:{after_date}")

    query = ' '.join(query_parts)

    print(f"📬 Lekérdezés ezzel a szűrővel: {query}")
    messages = []
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages.extend(response.get('messages', []))

        while 'nextPageToken' in response:
            response = service.users().messages().list(
                userId=user_id,
                q=query,
                pageToken=response['nextPageToken']
            ).execute()
            messages.extend(response.get('messages', []))

        print(f"📦 Archiválandó levelek száma: {len(messages)}")

        for i, msg in enumerate(messages, start=1):
            try:
                service.users().messages().modify(
                    userId=user_id,
                    id=msg['id'],
                    body={'removeLabelIds': ['INBOX']}
                ).execute()
                if i % 100 == 0:
                    print(f"🔄 {i} levél feldolgozva...")
            except Exception as e:
                print(f"⚠️ Hiba a(z) {msg['id']} levél archiválásánál: {e}")

        print("✅ Minden kiválasztott levél archiválva.")

    except Exception as e:
        print(f"❌ Hiba történt a levelek lekérdezése közben: {e}")

if __name__ == '__main__':
    service = gmail_authenticate()

    # Példa beállítások:
    archive_filtered_emails(
        service,
        exclude_starred=True,         # Csillagozott levelek maradnak
        exclude_important=True,       # Fontos levelek maradnak
        only_read=True,               # Csak olvasott levelek
        before_date="2024/12/31",     # 2024 vége előtti levelek
        after_date="2022/01/01"       # 2022-től kezdve
    )
