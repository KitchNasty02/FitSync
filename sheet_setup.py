import json
from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    create_sheet_in_folder,
    share_sheet_with_user
)

ADMIN_EMAIL = "connorkitch10@gmail.com"

# Load user accounts
with open("config/accounts.json", "r") as file:
    accounts = json.load(file)

# Initialize services
gc = get_gspread_client()
drive_service = get_drive_service()

# Get FitSync folder
folder_id = ensure_fitsync_folder(drive_service)

# Process each user
for name, data in accounts.items():
    sheet_id, sheet_url = create_sheet_in_folder(gc, drive_service, name, folder_id)
    share_sheet_with_user(drive_service, sheet_id, data["google_email"], ADMIN_EMAIL)
    print(f"Sheet ready for {name}: {sheet_url}")