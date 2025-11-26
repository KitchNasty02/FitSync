# FitSync

FitSync is a Python program that uses the public Garmin API to pull user activities and format them nicely in Google Sheets. This was made for tracking and analytics of my family's activities.

### How it works:
- user accounts are saved locally with encrypted passwords
- daily_sync_all.py is run daily via Windows Task Scheduler
- init_sync files are used to initialize an account manually (by date or number of activities)


## Next Additions
 - analytics graphs on top


## TODO Bug Fixes
 - Week labels are not merging to the previous week label if they are the same
