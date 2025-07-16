from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    create_sheet_in_folder,
    share_sheet_with_user
)

# Config info
TEST_USER = "joshkitchin@gmail.com"
ADMIN_EMAIL = "connorkitch10@gmail.com"
USERNAME = "Josh Kitchin"

# Initialize services
gc = get_gspread_client()
drive_service = get_drive_service()

# Create folder and sheet
folder_id = ensure_fitsync_folder(drive_service)
sheet_id, sheet_url = create_sheet_in_folder(gc, drive_service, USERNAME, folder_id)

# Share sheet with users
share_sheet_with_user(drive_service, sheet_id, TEST_USER, ADMIN_EMAIL)

# Done!
print(f"Sheet created: {sheet_url}")



# TODO:
# - make a new sheet from accounts.json
