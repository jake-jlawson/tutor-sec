
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# API CONFIGURATION
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = "apis/GoogleCalendar/credentials.json"
TOKEN_PATH = "apis/GoogleCalendar/token.json"


class GoogleCalendar:
    def __init__(self, credentials_path=CREDENTIALS_PATH, token_path=TOKEN_PATH, scopes=CALENDAR_SCOPES):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self.service = self.connect()

    def connect(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        try: # Try to build the service
            return build("calendar", "v3", credentials=creds)
        
        except HttpError as error: # If an error occurs, print it and return False
            print(f"An error occurred: {error}")
            return False
