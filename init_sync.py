from utils.garmin_fetch import get_garmin_client, fetch_all_workouts
import json

# sync all workouts on all accounts
def init_sync_all():
    # load all user accounts
    with open("config/accounts.json", "r") as file:
        accounts = json.load(file)

    # get workout data from each account
    for name, data in accounts.items():
        
        try:
            username, password = data["username"], data["password"]
            client = get_garmin_client(username, password)

            workouts = fetch_all_workouts(client)
            print(f"Fetched {len(workouts)} workouts for {username}")

        except Exception as e:
            print(f"Error fetching {name}'s data: {e}")

