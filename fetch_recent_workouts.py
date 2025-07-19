from utils.garmin_fetch import get_garmin_client, fetch_workouts, fetch_all_workouts
import json

# Load user accounts
with open("config/accounts.json", "r") as file:
    accounts = json.load(file)


for name, data in accounts.items():
    
    try:
        username, password = data["username"], data["password"]
        # print(f"Username: {username}, Password: {password}")
        client = get_garmin_client(username, password)


        #workouts = fetch_workouts(client, days=30)
        workouts = fetch_all_workouts(client)
        print(f"Fetched {len(workouts)} workouts")
        # print(workouts)

    except Exception as e:
        print(f"Error fetching {name}'s data: {e}")
