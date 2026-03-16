from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import datetime
import logging
import argparse
import time

# --- Logging beállítása (fájlba és konzolra is) ---
logging.basicConfig(
    filename='archiver.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# Scope: csak az INBOX label eltávolításához szükséges minimum
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def gmail_authenticate():
    """Google OAuth2 hitelesítés, token cache-eléssel."""
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
    after_date=None,
    dry_run=False
):
    """
    Gmail levelek archiválása szűrők alapján.

    Args:
        service: Gmail API service objektum
        exclude_starred (bool): Csillagozott levelek kizárása (alapértelmezett: True)
        exclude_important (bool): Fontos levelek kizárása (alapértelmezett: True)
        only_read (bool): Csak olvasott levelek archiválása (alapértelmezett: True)
        before_date (str): Ennél régebbi levelek archiválása (YYYY/MM/DD), pl. '2024/12/31'
        after_date (str): Ennél újabb levelek archiválása (YYYY/MM/DD), pl. '2022/01/01'
        dry_run (bool): Ha True, csak listázás, archiválás nélkül
    """
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

    logging.info(f"Lekérdezés ezzel a szűrővel: {query}")
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

        logging.info(f"Archiválandó levelek száma: {len(messages)}")

        # --- Dry-run mód: csak listáz, nem módosít ---
        if dry_run:
            logging.info("[DRY-RUN] Nem történt módosítás. Futtasd --dry-run nélkül az éles archiváláshoz.")
            return

        # --- Megerősítés kérése véletlen futtatás ellen ---
        confirm = input(f"\n⚠️  {len(messages)} levél archiválódna. Folytatod? (igen/nem): ")
        if confirm.strip().lower() != 'igen':
            logging.info("Archiválás megszakítva a felhasználó által.")
            print("Megszakítva.")
            return

        # --- Archiválás rate limiting védelemmel ---
        for i, msg in enumerate(messages, start=1):
            try:
                service.users().messages().modify(
                    userId=user_id,
                    id=msg['id'],
                    body={'removeLabelIds': ['INBOX']}
                ).execute()
                if i % 100 == 0:
                    logging.info(f"{i}/{len(messages)} levél feldolgozva...")
                # Rate limiting: 50 levelenként 1 mp szünet
                if i % 50 == 0:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Hiba a(z) {msg['id']} levél archiválásánál: {e}")

        logging.info("Minden kiválasztott levél sikeresen archiválva.")

    except Exception as e:
        logging.error(f"Hiba történt a levelek lekérdezése közben: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Gmail Archiver – levelek archiválása szűrők alapján'
    )
    parser.add_argument(
        '--before', default=None,
        help='Ennél régebbi levelek archiválása (YYYY/MM/DD), pl. 2024/12/31'
    )
    parser.add_argument(
        '--after', default=None,
        help='Ennél újabb levelek archiválása (YYYY/MM/DD), pl. 2022/01/01'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Csak listázás, archiválás nélkül – biztonságos teszteléshez'
    )
    parser.add_argument(
        '--include-starred', action='store_true',
        help='Csillagozott levelek is archiválódjanak'
    )
    parser.add_argument(
        '--include-important', action='store_true',
        help='Fontos levelek is archiválódjanak'
    )
    parser.add_argument(
        '--include-unread', action='store_true',
        help='Olvasatlan levelek is archiválódjanak'
    )
    args = parser.parse_args()

    service = gmail_authenticate()

    archive_filtered_emails(
        service,
        exclude_starred=not args.include_starred,
        exclude_important=not args.include_important,
        only_read=not args.include_unread,
        before_date=args.before,
        after_date=args.after,
        dry_run=args.dry_run
    )
