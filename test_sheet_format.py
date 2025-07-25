from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    ensure_sheet_in_folder
)
from utils.garmin_fetch import get_garmin_client  # Optional if needed for auth checks
from format_utils import format_sheet, set_font_and_size  # Make sure formatting funcs are imported
import json

def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)
    
def test_sheet_formatting():
    accounts = load_accounts()
    gc = get_gspread_client()
    drive_service = get_drive_service()
    folder_id = ensure_fitsync_folder(drive_service)

    # Just pick the first account for testing
    name, data = next(iter(accounts.items()))
    print(f"Testing formatting for {name}...")

    # Access sheet
    sheet, sheet_url = ensure_sheet_in_folder(gc, drive_service, name, data["google_email"], folder_id)

    spreadsheet = gc.open_by_url(sheet_url)
    sheet = spreadsheet.sheet1  # or use .worksheet("Sheet1") if it's named


    # Run formatting
    format_sheet(sheet)
    set_font_and_size(sheet)

    print(f"Sheet formatted successfully for {name}!")

if __name__ == "__main__":
    test_sheet_formatting()