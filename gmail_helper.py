import base64

from datetime import datetime
from email.utils import parsedate_to_datetime

from googleapiclient.errors import HttpError

def load_keywords(filepath='keywords.txt') -> list:
    try:
        with open(filepath, 'r') as f:
            keywords = [line.strip().lower() for line in f if line.strip()]
        return keywords
    except FileNotFoundError:
        print(f"Keyword file {filepath} not found. Using default keywords.")
        return ["internship", "intern", "application"]

def get_messages(service, user_id='me', label_ids=None, folder_name='INBOX', max_results=5) -> list:
    messages = []
    next_page_token = None

    if folder_name:
        label_results = service.users().labels().list(userId=user_id).execute()
        labels = label_results.get('labels',[])
        folder_label_id = next((label['id'] for label in labels 
                               if label['name'].lower() == folder_name.lower()), None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids = [folder_label_id]
        else:
            raise ValueError(f"Folder '{folder_name}' not found.")
    
    while True:
        result = service.users().messages().list(
            userId = user_id,
            labelIds= label_ids,
            maxResults=min(500,max_results - len(messages)) if max_results else 500,
            pageToken=next_page_token
        ).execute()

        message_ids = result.get("messages", [])

        for msg in message_ids:
            full_message = service.users().messages().get(
                userId=user_id,
                id=msg["id"]
            ).execute()
            messages.append(full_message)

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break
    
    return messages[:max_results] if max_results else messages

def is_internship_email(message, keywords) -> bool:
    headers = message['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    
    subject_lower = subject.lower()

    if any(keyword in subject_lower for keyword in keywords):
        return True
    
    try:
        if 'data' in message['payload']['body']:
            body_data = message['payload']['body']['data']
            body = base64.urlsafe_b64decode(body_data).decode(errors='ignore').lower()
            if any(keyword in body for keyword in keywords):
                return True
    except Exception:
        pass

    return False

def get_or_create_label(service, label_name = 'Career/Internships'):
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    
    label_obj = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }
    new_label = service.users().labels().create(userId="me", body=label_obj).execute()
    return new_label["id"]

def label_message(service, msg_id, label_id) -> None:
    service.users().messages().modify(
        userId = "me",
        id=msg_id,
        body={"addLabelIds": [label_id]}
    ).execute()

def debug_print_message(message):
    """
    Prints key info (ID, Subject, From, Date) for debugging Gmail API messages.
    """
    headers = message.get("payload", {}).get("headers", [])

    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
    sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "")
    date = next((h["value"] for h in headers if h["name"].lower() == "date"), "")

    print("------ EMAIL DEBUG ------")
    print(f"ID: {message.get('id', '')}")
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print(f"Date: {date}")
    print("-------------------------\n")