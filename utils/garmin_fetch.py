from garminconnect import Garmin
from datetime import datetime, timedelta
from utils.encryption import decrypt_password, load_key
import requests
import random
import time

def get_garmin_client(email, encrypted_pw):
    try_counter = 0
    while try_counter < 5:
        try:
            key = load_key()
            decrypted_pw = decrypt_password(encrypted_pw, key)
            client = Garmin(email, decrypted_pw)
            client.login()
            return client
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                try_counter += 1
                sleep_time = random.randint(2, 8)
                print(f"Rate limit hit (try {try_counter}). Sleeping {sleep_time} minutes...")
                time.sleep(sleep_time * 60)
            else:
                print(f"Exception: {e}")

    return None


def fetch_workouts(client, days=30, date=None):
    try:
        today = datetime.now().date()

        if date:
            start = datetime.strptime(date, "%m/%d/%Y")
        else:
            start = today - timedelta(days=days)

        activities = client.get_activities_by_date(start.isoformat(), today.isoformat())
        return activities

    except Exception as e:
        print(f"Error fetching workouts: {e}")
        return []



def fetch_all_workouts(client, max_activities=1000):
    
    workouts = []
    start = 0

    while True:
        batch = client.get_activities(start, 20)
        if not batch:
            break
        workouts.extend(batch)
        start += 20
        if len(workouts) >= max_activities:
            break

    return workouts