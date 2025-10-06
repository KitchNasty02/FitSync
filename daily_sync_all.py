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
from sync_sheet import sync_sheet, get_last_workout_date
from datetime import date, datetime
import json
import os

log_file = "config/last_run.log"

def record_last_run():
    now = datetime.now()
    with open(log_file, "w") as f:
        f.write(now.isoformat())

def get_last_run():
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            timestamp_str = f.read()
        return datetime.fromisoformat(timestamp_str)
    return None

def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)
    

# use this when first making the accounts
def daily_sync_all():
    
    accounts = load_accounts()
    
    # initialize google services
    gc = get_gspread_client()
    drive_service = get_drive_service()
    folder_id = ensure_fitsync_folder(drive_service)

    # get workout data from each account
    for name, data in accounts.items():
        
        try:
            username, password = data["username"], data["password"]
            client = get_garmin_client(username, password)
            
            # skip if client could not log in (incorrect credentials)
            if not client:
                continue

            """
            get the last time script was run
            sync back through this date so it will update all workouts if the script fails to run
            """
            last_run = get_last_run()
            
            # get todays workouts (syncs at 11:59pm via windows scheduler)
            today = date.today()
            today = datetime.strftime(today, "%m/%d/%Y")
            last_run = datetime.strftime(last_run, "%m/%d/%Y")

            # last_run = "10/01/2025"

            print(f"Fetching workouts from {last_run} to {today}")
            workouts = fetch_workouts(client, date=last_run)
            print(f"Fetched {len(workouts)} workouts for {username}")

            # Access sheet
            _, sheet_url = ensure_sheet_in_folder(gc, drive_service, name, data["google_email"], folder_id)
            spreadsheet = gc.open_by_url(sheet_url)

            sync_sheet(spreadsheet, workouts, season_ranges=data.get("season_ranges"))

        except Exception as e:
            print(f"Error fetching {name}'s data: {e}")

    record_last_run()


daily_sync_all()