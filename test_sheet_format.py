from utils.drive_setup import (
    get_gspread_client,
    get_drive_service,
    ensure_fitsync_folder,
    ensure_sheet_in_folder
)
from utils.garmin_fetch import get_garmin_client, fetch_all_workouts  # Optional if needed for auth checks
from format_utils import format_sheet, set_font_and_size  # Make sure formatting funcs are imported
from sync_sheet import sync_sheet, update_header
import json

def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)\
        
import datetime
test_data = [
    # August Activities
    {
        "activityId": 1012345678,
        "activityName": "Run",
        "startTimeLocal": "2025-08-01 06:30:00",
        "startTimeGMT": "2025-08-01 12:30:00",
        "duration": 1800.0,
        "distance": 5000.0,
        "averageHR": 140,
        "rpe": 6,
        "description": "Morning tempo run",
        "sportType": {"typeId": 1, "typeKey": "running"}
    },
    {
        "activityId": 1012345679,
        "activityName": "Swim",
        "startTimeLocal": "2025-08-01 17:00:00",
        "startTimeGMT": "2025-08-01 23:00:00",
        "duration": 2400.0,
        "distance": 1200.0,
        "averageHR": 130,
        "rpe": 5,
        "description": "Pool intervals",
        "sportType": {"typeId": 2, "typeKey": "swimming"}
    },
    {
        "activityId": 1012345681,
        "activityName": "Strength",
        "startTimeLocal": "2025-08-03 08:00:00",
        "startTimeGMT": "2025-08-03 14:00:00",
        "duration": 3600.0,
        "distance": 0.0,
        "averageHR": 120,
        "rpe": 7,
        "description": "Full body lifting session",
        "sportType": {"typeId": 4, "typeKey": "strength_training"}
    },
    {
        "activityId": 1012345682,
        "activityName": "Run",
        "startTimeLocal": "2025-08-04 07:00:00",
        "startTimeGMT": "2025-08-04 13:00:00",
        "duration": 1500.0,
        "distance": 4000.0,
        "averageHR": 135,
        "rpe": 5,
        "description": "Recovery run",
        "sportType": {"typeId": 1, "typeKey": "running"}
    },

    # July Activities
    {
        "activityId": 1012345680,
        "activityName": "Bike",
        "startTimeLocal": "2025-07-31 18:00:00",
        "startTimeGMT": "2025-08-01 00:00:00",
        "duration": 3600.0,
        "distance": 20000.0,
        "averageHR": 125,
        "rpe": 4,
        "description": "Evening ride",
        "sportType": {"typeId": 3, "typeKey": "cycling"}
    },
    {
        "activityId": 1012345683,
        "activityName": "Swim",
        "startTimeLocal": "2025-07-29 07:30:00",
        "startTimeGMT": "2025-07-29 13:30:00",
        "duration": 1800.0,
        "distance": 1000.0,
        "averageHR": 128,
        "rpe": 5,
        "description": "Easy morning swim",
        "sportType": {"typeId": 2, "typeKey": "swimming"}
    },
    {
        "activityId": 1012345684,
        "activityName": "Bike",
        "startTimeLocal": "2025-07-27 09:00:00",
        "startTimeGMT": "2025-07-27 15:00:00",
        "duration": 5400.0,
        "distance": 25000.0,
        "averageHR": 132,
        "rpe": 6,
        "description": "Weekend long ride",
        "sportType": {"typeId": 3, "typeKey": "cycling"}
    }
]

    
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
    # format_sheet(sheet, test_data)
    update_header(sheet)
    sync_sheet(sheet, test_data)
    # set_font_and_size(sheet)

    print(f"Sheet formatted successfully for {name}!")

if __name__ == "__main__":
    test_sheet_formatting()