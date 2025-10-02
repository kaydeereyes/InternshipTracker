from datetime import datetime
from email import encoders

from googleapiclient.errors import HttpError
#from googleapiclient.discovery import build

def get_messages(service, user_id='me', label_ids=None, folder_name='INBOX', max_results=5):
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

        messages.extend(result.get('messages', []))

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break
    
    return messages[:max_results] if max_results else messages

    