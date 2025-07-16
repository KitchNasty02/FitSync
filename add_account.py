from utils.encryption import generate_key, load_key, encrypt_password
import json
import os


# saves username and encrypted password to accounts.json
def save_account(name, username, encrypted_pw, google_email, path="config/accounts.json"):
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
        "google_email": google_email
    }

    # save
    with open(path, "w") as file:
        json.dump(accounts, file, indent=4)


name = input("Enter Persons Name: ")
username = input("Enter GarminConnect Email: ")
password = input("Enter Password: ")
google_email = input("Enter Google Email: ")

key = load_key()
encrypted_password = encrypt_password(password, key)
save_account(name, username, encrypted_password, google_email)
print("Account Saved.")
