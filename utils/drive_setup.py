from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import gspread
import os


# Scopes for Google Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_gspread_client():
    # Authenticate using local token from gspread (OAuth flow)
    return gspread.oauth()


def get_drive_service():
    token_path = "config/token.json"
    if not os.path.exists(token_path):
        raise FileNotFoundError("Token file missing. Run OAuth to authorize first.")

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    return build("drive", "v3", credentials=creds)


def ensure_fitsync_folder(drive_service, folder_name="FitSync Sheets"):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive_service.files().create(body=metadata, fields="id").execute()
    print(f"Created FitSync folder: {folder['id']}")
    return folder["id"]


def create_sheet_in_folder(gc, drive_service, username, folder_id):
    sheet_name = f"{username} Fitness Log"
    print(f"Searching for sheet named: {sheet_name}")

    # check if sheet already exists
    query = (
        f"name = '{sheet_name}' and "
        f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
        f"'{folder_id}' in parents"
    )

    result = drive_service.files().list(q=query, fields="files(id, name)").execute()
    existing_files = result.get("files", [])

    if existing_files:
        sheet_id = existing_files[0]["id"]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        print(f"Sheet already exists for {username}: {sheet_url}")
        return sheet_id, sheet_url

    # create new sheet
    sheet = gc.create(sheet_name)
    sheet_id = sheet.id
    
    # Move the Sheet into the FitSync folder
    drive_service.files().update(
        fileId=sheet_id,
        addParents=folder_id,
        fields="id, parents"
    ).execute()

    print(f"Created and organized sheet for {username}")
    return sheet_id, sheet.url


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