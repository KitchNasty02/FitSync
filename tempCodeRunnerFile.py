from utils.drive_setup import (
    get_drive_service,
    ensure_fitsync_folder,
    create_sheet_in_folder,
    share_sheet_with_user
)

import json

# Load user info
with open("config/accounts.json", "r") as file:
    accounts = json.load(file)

drive_service = get_drive_service()
folder_id = ensure_fitsync_folder(drive_service)

for name, data in accounts.items():
    sheet_id = create_sheet_in_folder(drive_service, name, folder_id)
    share_sheet_with_user(drive_service, sheet_id, data["google_email"], "connorkitch10@gmail.com")