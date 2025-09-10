import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/spreadsheets.readonly"]

def main():
    creds = None

    if os.path.exists("tokens.json"):
        creds = Credentials.from_authorized_user_file("tokens.json", SCOPES)

        if not creds or creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppsFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("tokens.json", "w") as token:
                token.write(creds.to_json())

    try:
        #Calls the Gmail & Sheets API
        gmail_service = build("gmail", "v1", credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        pass

    except HttpError as error:
        print(f"An error occurred: {error}")



if __name__ == "__main__":
    main()