from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread
import os

ADMIN_EMAIL = "connorkitch10@gmail.com"

# scopes for google sheets and drive
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_gspread_client():
    return gspread.oauth(
        credentials_filename="config/credentials.json",
        authorized_user_filename="config/token.json"
    )


def get_drive_service():
    token_path = "config/token.json"
    if not os.path.exists(token_path):
        raise FileNotFoundError("Token file missing. Run OAuth to authorize first.")

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # refresh token if token is expired
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # save the refreshed token back to disk
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


# make sure fitsync folder exists
def ensure_fitsync_folder(drive_service, folder_name="FitSync Sheets"):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", [])

    # return folder if exists
    if folders:
        return folders[0]["id"]

    # make new folder if it does not exist
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive_service.files().create(body=metadata, fields="id").execute()
    print(f"Created FitSync folder: {folder['id']}")
    return folder["id"]


# create and share sheet if one does not exist
def ensure_sheet_in_folder(gc, drive_service, username, user_email, folder_id):
    sheet_name = f"{username} Training Log"
    print(f"Searching for sheet named: {sheet_name}")

    # check if sheet already exists
    query = (
        f"name = '{sheet_name}' and "
        f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
        f"'{folder_id}' in parents"
    )

    result = drive_service.files().list(q=query, fields="files(id, name)").execute()
    existing_files = result.get("files", [])

    # return sheet if it already exists
    if existing_files:
        sheet_id = existing_files[0]["id"]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        print(f"Sheet already exists for {username}: {sheet_url}")
        
        return sheet_id, sheet_url

    # create new sheet if one does not exist
    sheet = gc.create(sheet_name)
    sheet_id = sheet.id
    
    # Move the Sheet into the FitSync folder
    drive_service.files().update(
        fileId=sheet_id,
        addParents=folder_id,
        fields="id, parents"
    ).execute()

    share_sheet_with_user(drive_service, sheet_id, user_email, ADMIN_EMAIL)
    print(f"Created and shared sheet for {username}")

    return sheet_id, sheet.url


# share sheet with a given google user
def share_sheet_with_user(drive_service, file_id, user_email, admin_email):
    permissions = [
        {
            "type": "user",
            "role": "writer",
            "emailAddress": user_email
        },
        {
            "type": "user",
            "role": "writer",
            "emailAddress": admin_email
        }
    ]

    for perm in permissions:
        drive_service.permissions().create(
            fileId=file_id,
            body=perm,
            sendNotificationEmail=True
        ).execute()

    print(f"Shared sheet with {user_email} and {admin_email}")




    