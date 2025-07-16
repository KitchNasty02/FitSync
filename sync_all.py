import json
from utils.encryption import load_key, decrypt_password
from utils.garmin_fetch import fetch_workouts, fetch_all_workouts
# from utils.sheet_writer import update_sheet 


# if true, syncs ALL workouts
INIT_MODE = False


def load_accounts(path="config/accounts.json"):
    with open(path, "r") as file:
        return json.load(file)


def sync_all_accounts():
    key = load_key()
    accounts = load_accounts()

    for username, creds in accounts.items():
        try:
            print(f"Syncing {username}...")
            decrypted_pw = decrypt_password(creds["password"], key)

            if not INIT_MODE:
                activities = fetch_workouts(creds["username"], decrypted_pw)
            else:
                activites = fetch_all_workouts(creds["username"], decrypted_pw)

            if activities:
                print(f"{len(activities)} workouts fetched for {username}")
                # update_sheet(username, activities)
            else:
                print(f"No workouts found for {username}")

        except Exception as e:
            print(f"Error syncing {username}: {e}")



if __name__ == "__main__":
    sync_all_accounts()




