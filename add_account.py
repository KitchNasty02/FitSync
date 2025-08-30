from utils.encryption import load_key, encrypt_password
from init_sync import init_sync
from datetime import datetime
import json
import os

# loop to get tab name and start date
def get_season_ranges():
    season_ranges = {}

    while True:
        season_name = input("Enter season name: ")
        start_day = input("Enter start day (DD): ")
        start_month = input("Enter start month (MM): ")
        start_year = input("Enter start year (YYYY): ")

        try:
            start_date_obj = datetime.strptime(f"{start_year}-{start_month}-{start_day}", "%Y-%m-%d")
            start_date = start_date_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date, try again.")
            continue

        tab_title = f"{season_name} {start_year}"

        if tab_title in season_ranges:
            print(f"Tab {tab_title} already exists, try a different one.")
            continue

        season_ranges[tab_title] = start_date

        user_input = input("Add another season? (y/n): ").lower()
        if user_input == 'n':
            break

    return season_ranges




# saves username and encrypted password to accounts.json
def save_account(name, username, encrypted_pw, google_email, season_ranges, path="config/accounts.json"):
    # load existing accounts
    if os.path.exists(path):
        with open(path, "r") as file:
            accounts = json.load(file)
    else:
        accounts = {}

    # add new user
    accounts[name] = {
        "name": name,
        "username": username,
        "password": encrypted_pw,
        "google_email": google_email,
        "season_ranges": season_ranges
    }

    # save
    with open(path, "w") as file:
        json.dump(accounts, file, indent=4)


name = input("Enter Persons Name: ")
username = input("Enter GarminConnect Email: ")
password = input("Enter CarminConnect Password: ")
google_email = input("Enter Google Email: ")
custom_tabs = input("Do you want custom tabs? (y/n -- default is each year)")
sync_type = input("How would you like to sync? (a=all, d=date, n=none)")
if sync_type == "d":
    sync_date = input("What date to start from? (mm/dd/yyyy)")


if custom_tabs == 'y':
    season_ranges = get_season_ranges()
else:
    season_ranges = None    # defaults to each year


key = load_key()
encrypted_password = encrypt_password(password, key)


account_preview = {
    "name": name,
    "username": username,
    "google_email": google_email,
    "season_ranges": season_ranges if season_ranges else "Default: yearly tabs"
}

print(json.dumps(account_preview, indent=4))
input("Save this account info?")

save_account(name, username, encrypted_password, google_email, season_ranges)
print("Account Saved.")

# initial sync
if sync_type == "a":
    init_sync(name, "all")
elif sync_type == "d":
    init_sync(name, "date", sync_date)
else:
    init_sync(name, "none")

print(f"{name}'s Account Synced")

