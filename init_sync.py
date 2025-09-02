from utils.garmin_fetch import (
    get_garmin_client, 
    fetch_all_workouts, 
    fetch_workouts
)
from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    ensure_sheet_in_folder
)
from sync_sheet import sync_sheet
import json


def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)
    

# sync an account that just got created
def init_sync(name, sync_type, date=None):
    
    accounts = load_accounts()

    if name not in accounts:
        print(f"Account '{name}' not found")
        return
    
    data = accounts[name]
    
    # initialize google services
    gc = get_gspread_client()
    drive_service = get_drive_service()
    folder_id = ensure_fitsync_folder(drive_service)

    try:
        username, password = data["username"], data["password"]
        client = get_garmin_client(username, password)
        
        workouts = []
        
        if sync_type == "all":
            workouts = fetch_all_workouts(client)
        elif sync_type == "date":
            workouts = fetch_workouts(client, date=date)
        else:
            print(f"Unknown sync type: {sync_type}")
            return
        
        
        print(f"Fetched {len(workouts)} workouts for {username}")

        # Access sheet
        _, sheet_url = ensure_sheet_in_folder(gc, drive_service, name, data["google_email"], folder_id)

        spreadsheet = gc.open_by_url(sheet_url)
        sync_sheet(spreadsheet, workouts, season_ranges=data.get("season_ranges"))

    except Exception as e:
        print(f"Error fetching {name}'s data: {e}")


init_sync("Ellie Kitchin", "date", "01/01/2025")


