from utils.encryption import load_key, encrypt_password
import json
import os


# saves username and encrypted password to accounts.json
def save_account(name, username, encrypted_pw, google_email, season_ranges, path="config/accounts.json"):
    # load existing accounts
    if os.path.exists(path):
        with open(path, "r") as file:
            accounts = json.load(file)
    else:
        accounts = {}

    # set season ranges
    if season_ranges == "year":
        account_ranges = {}
    else:
        # "season_ranges": {
        #     "XC": "08-15",
        #     "Indoor Track": "11-21",
        #     "Outdoor Track": "03-01",
        #     "Summer": "06-01"
        # } # use this to make the tabs. Maybe add year since date will change
        pass

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

# check and get tab dates
if custom_tabs == 'y':
    # loop to get tab name and start date
    pass
else:
    season_ranges = "year"



key = load_key()
encrypted_password = encrypt_password(password, key)
save_account(name, username, encrypted_password, google_email, season_ranges)
print("Account Saved.")
