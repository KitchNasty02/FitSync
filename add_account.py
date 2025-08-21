from utils.encryption import load_key, encrypt_password
import json
import os

# loop to get tab name and start date
def get_season_ranges():
    season_ranges = {}

    while user_input != 'n':
        season_name = input("Enter season name: ")
        start_day = input("Enter start day: ")
        start_month = input("Enter start month: ")
        start_year = input("Enter start year: ")

        tab_title = f"{season_name} {start_year}"
        start_date = f""



# saves username and encrypted password to accounts.json
def save_account(name, username, encrypted_pw, google_email, season_ranges, path="config/accounts.json"):
    # load existing accounts
    if os.path.exists(path):
        with open(path, "r") as file:
            accounts = json.load(file)
    else:
        accounts = {}

    # # set season ranges
    # if season_ranges == "year":
    #     account_ranges = {}
    # else:
        # "season_ranges": {
        #     "XC": "08-15",
        #     "Indoor Track": "11-21",
        #     "Outdoor Track": "03-01",
        #     "Summer": "06-01"
        # } # use this to make the tabs. Maybe add year since date will change
        # account_ranges = season_ranges
        # pass

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
password = input("Enter Password: ")
google_email = input("Enter Google Email: ")
custom_tabs = input("Do you want custom tabs? (y/n -- default is each year)")

if custom_tabs == 'y':
    season_ranges = get_season_ranges()
else:
    season_ranges = None    # defaults to each year



key = load_key()
encrypted_password = encrypt_password(password, key)
save_account(name, username, encrypted_password, google_email, season_ranges)
print("Account Saved.")
