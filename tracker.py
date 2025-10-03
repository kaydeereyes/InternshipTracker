import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import gmail_helper as gh

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

def get_credentials():
    creds = None
    # Load saved token if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If no valid token, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = get_credentials()

    keywords = gh.load_keywords()

    try:
        #Calls the Gmail & Sheets API
        gmail_service = build("gmail", "v1", credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        messages = gh.get_messages(gmail_service, max_results=5)

        for m in messages:
            if gh.is_internship_email(full_message, keywords):
                print('INTERNSHIP')

        
            

    except HttpError as error:
        print(f"An error occurred: {error}")



if __name__ == "__main__":
    main()