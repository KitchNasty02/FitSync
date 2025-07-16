from garminconnect import Garmin
from datetime import datetime, timedelta


def fetch_workouts(client, days=30):

    try:
        today = datetime.now().date()
        start = today - timedelta(days=days)

        activities = client.get_activities_by_date(start.isoformat(), today.isoformat())
        return activities

    except Exception as e:
        print(f"Error fetching workouts")
        return []




def fetch_all_workouts(client, max_activities=500):
    
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