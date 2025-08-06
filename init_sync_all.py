from utils.garmin_fetch import get_garmin_client, fetch_all_workouts
from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    ensure_sheet_in_folder
)
from sync_sheet import sync_sheet, update_header
import json


def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)
    

# sync all workouts on all accounts
def init_sync_all():
    
    accounts = load_accounts()
    
    # initialize google services
    gc = get_gspread_client()
    drive_service = get_drive_service()
    folder_id = ensure_fitsync_folder(drive_service)

    # get workout data from each account
    for name, data in accounts.items():
        
        try:
            # make sure sheet is created for the user
            ensure_sheet_in_folder(gc, drive_service, name, data["google_email"], folder_id)

            username, password = data["username"], data["password"]
            client = get_garmin_client(username, password)
            
            # skip if client could not log in (incorrect credentials)
            if not client:
                continue

            workouts = fetch_all_workouts(client)
            print(f"Fetched {len(workouts)} workouts for {username}")

            # Access sheet
            sheet, sheet_url = ensure_sheet_in_folder(gc, drive_service, name, data["google_email"], folder_id)

            spreadsheet = gc.open_by_url(sheet_url)
            sheet = spreadsheet.sheet1  # or use .worksheet("Sheet1") if it's named

            update_header(sheet)
            sync_sheet(sheet, workouts)

            print(f"Sheet formatted successfully for {name}!")


        except Exception as e:
            print(f"Error fetching {name}'s data: {e}")



init_sync_all()