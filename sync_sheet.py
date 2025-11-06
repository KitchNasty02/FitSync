from gspread_formatting import set_frozen, set_column_width, set_row_height
from collections import defaultdict
from datetime import datetime, timedelta
import time
import re

COOLDOWN_DURATION = 120

# ensures the api request do not fail from the rate limit
def safe_request(func, *args, max_sleep=60, **kwargs):
    # sleep time increases each time limit is hit
    sleep_times = [10, 15, 30, 45, max_sleep]
    for sleep_time in sleep_times:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit hit. Cooling down for {sleep_time}s...")
                for remaining in range(sleep_time, 0, -1):
                    print(f"Resuming in {remaining}s...", end="\r")
                    time.sleep(1)
                print("Cooldown complete. Retrying now.")
            else:
                raise e
    raise RuntimeError("Exceeded retry attempts due to persistent 429 errors.")


# determines how many data columns there are
NUM_COLS = 10


# colors
MONTH_COLOR = (207, 226, 243)
HEADERS_COLOR = (159, 197, 232)
# WEEK_COLORS = [
#     {"red": 0.90, "green": 0.95, "blue": 1.0},  # light blue
#     {"red": 0.90, "green": 1.0, "blue": 0.90}   # light green
# ]
WEEK_COLORS = [
    {"red": 0.95, "green": 0.95, "blue": 0.95},  # medium gray
    {"red": 1.0,  "green": 1.0,  "blue": 1.0}    # white
]

WHITE = {"red": 1.0,  "green": 1.0,  "blue": 1.0}

ROW_HEIGHT = 30

# convert to better labels in sheet
TYPEKEY_MAP = {
    "running": "Run",
    "Track_Running": "Run",
    "cycling": "Bike",
    "Indoor_Cardio": "Bike",
    "swimming": "Swim",
    "lap_swimming": "Swim",
    "strength_training": "Strength",
    "cardio_training": "Cardio",
    "walking": "Walk",
    "hiking": "Hike",
    "treadmill_running": "Run",
    "indoor_cycling": "Bike",
    "other": "Other"
}


def update_header(sheet):
    # TODO: Add update for weekly mileage graphs and stuff
    # would shift the frozen rows down

    headers = ["", "", "Date", "Activity", "Distance", "Time", "Avg Pace", "Avg HR", "RPE", "Description"]
    safe_request(sheet.update, "A1", [headers])
    safe_request(sheet.format, "A1:J1", {
        "horizontalAlignment": "CENTER", 
        "backgroundColor": rgb_to_normalized(HEADERS_COLOR),
        "textFormat": {
            "fontSize": 11,
            "bold": True,
            "fontFamily": "Times New Roman"}
        })
    safe_request(set_frozen, sheet, rows=1)



def sync_sheet(spreadsheet, workout_data, season_ranges=None):
    tab_map = {}

    # group workouts by tab
    tab_groups = defaultdict(lambda: defaultdict(list)) # {tab_title: {date: [workouts]}}

    for w in workout_data:
        if isinstance(w["startTimeLocal"], str):
            w["startTimeLocal"] = datetime.strptime(w["startTimeLocal"], "%Y-%m-%d %H:%M:%S")
        
        workout_date = w["startTimeLocal"].date()
        tab_title = get_tab_name(workout_date, season_ranges)
        tab_groups[tab_title][workout_date].append(w)

    sorted_tabs = sorted(tab_groups.keys(), key=lambda t: get_tab_sort_key(t, season_ranges))
    
    for tab_title in sorted_tabs:
        daily_groups = tab_groups[tab_title]

        # get or create tab
        if tab_title not in tab_map:
            try:
                tab_map[tab_title] = spreadsheet.worksheet(tab_title)
            except:
                # create tab with a starting 20 rows and NUM_COLS columns
                tab_map[tab_title] = spreadsheet.add_worksheet(title=tab_title, rows=20, cols=NUM_COLS)
                update_header(tab_map[tab_title])
                set_column_widths(tab_map[tab_title])

        sheet = tab_map[tab_title]

        latest_date = get_last_workout_date(sheet)

        # delete rows related to latest date in case of previous errors
        # if latest_date:
        #     rows_to_delete = find_rows_with_date(sheet, latest_date)
        #     for row_index in reversed(rows_to_delete):
        #         try:
        #             safe_request(sheet.delete_rows, row_index)
        #         except Exception as e:
        #             print(f"Failed to delete row {row_index}: {e}")

        unsynced_dates = [
            date for date in daily_groups
            # get dates that are before the last synced one
            if not latest_date or date > latest_date
        ]
        if not unsynced_dates:
            print(f"Tab '{tab_title}' is already up to date.")
            continue

        
        
        # get first date in tab
        anchor_date = get_first_date(sheet, unsynced_dates)

        print(f"Last date entered: {latest_date}, first date in sheet: {anchor_date}")
            
        inserted_months = get_existing_month_dividers(sheet)

        # Group workouts by week
        week_groups = defaultdict(lambda: defaultdict(list))
        for date in unsynced_dates:
            week_index = get_week_index(date, anchor_date)
            week_groups[week_index][date] = daily_groups[date]

        # row after the last one with info
        insert_index = len(sheet.get_all_values()) + 1

        # get full range of weeks for the tab
        min_week = min(week_groups.keys())
        max_week = max(week_groups.keys())

        # goes through workouts by date over all weeks (even if no workouts exist)
        for week_index in range(min_week, max_week + 1):
            week_color = WEEK_COLORS[week_index % 2]
            week_data = week_groups.get(week_index, {})  # may be empty

            block_start = insert_index
            week_label_blocks = []

            # insert blank row if no workouts exist for the week
            if not week_data:
                safe_request(sheet.insert_row, [""] * 9, index=insert_index)
                safe_request(sheet.format, f"A{insert_index}:I{insert_index}", {
                    "backgroundColor": week_color,
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"fontSize": 10}
                })
                safe_request(set_row_height, sheet, str(insert_index), ROW_HEIGHT)
                week_label_blocks.append((insert_index, insert_index))
                insert_index += 1

            else:
                for date in sorted(week_data.keys()):
                    workouts = week_data[date]
                    month_key = date.strftime('%Y-%m')

                    # Insert month divider if needed
                    if month_key not in inserted_months:
                        # close previous bock for the week if the month changes
                        if block_start < insert_index:
                            week_label_blocks.append((block_start, insert_index - 1))
                        insert_month_divider(sheet, date, insert_index)
                        inserted_months.add(month_key)
                        insert_index += 1
                        block_start = insert_index

                    # Insert workouts
                    for i, workout in enumerate(workouts):
                        insert_row(sheet, workout, date, insert_index, i == 0, row_color=week_color)
                        insert_index += 1

                    # Merge date cells if multiple workouts in a day
                    if len(workouts) > 1:
                        safe_request(sheet.merge_cells, f"C{insert_index - len(workouts)}:C{insert_index - 1}")
                        safe_request(sheet.format, f"C{insert_index - len(workouts)}", {"verticalAlignment": "MIDDLE"})

            # Final block for this week
            if block_start < insert_index:
                week_label_blocks.append((block_start, insert_index - 1))

            # Apply vertical week labels per block
            for block_start, block_end in week_label_blocks:
                # make indention column white
                safe_request(sheet.format, f"A{block_start}:A{block_end}", {"backgroundColor": WHITE})

                safe_request(sheet.update, f"B{block_start}", [[f"W{week_index + 1}"]])
                if block_end > block_start:
                    safe_request(sheet.merge_cells, f"B{block_start}:B{block_end}")

                safe_request(sheet.format, f"B{block_start}", {
                    "textRotation": {"angle": 90},
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "textFormat": {"bold": True}
                })

        print(f"Inserted {sum(len(v) for v in daily_groups.values())} new workouts into '{tab_title}'")


def insert_month_divider(sheet, date, insert_index):
    divider_text = date.strftime('%B %Y')
    
    safe_request(sheet.insert_row, [divider_text], index=insert_index)
    safe_request(set_row_height, sheet, str(insert_index), ROW_HEIGHT) # set row height
    safe_request(sheet.merge_cells, f"A{insert_index}:J{insert_index}")

    safe_request(sheet.format, f"A{insert_index}:G{insert_index}", {
        "backgroundColor": rgb_to_normalized(MONTH_COLOR),
        "horizontalAlignment": "LEFT",
        "verticalAlignment": "MIDDLE",
        "textFormat": {"fontSize": 10, "bold": True}
    })



def insert_row(sheet, workout, date, insert_index, is_first_row, row_color):
    
    raw_type = workout.get("activityType", {}).get("typeKey", "")
    activity_label = TYPEKEY_MAP.get(raw_type, raw_type.title())

    distance_miles = round(workout.get("distance", 0) / 1609.34, 2)
    duration_sec = workout.get("duration", 0)
    duration = sec_to_hms(workout.get("duration", 0))

    if distance_miles > 0:
        pace_sec_per_mile = duration_sec / distance_miles
        minutes = int(pace_sec_per_mile // 60)
        seconds = int(round(pace_sec_per_mile % 60))
        avg_pace = f"{minutes}:{seconds:02d}"
    else:
        avg_pace = ""

    date_label = date.strftime('%m/%d') if is_first_row else ""
    avg_hr = workout.get("averageHR", "")
    description = workout.get("description", "")

    row = [
        "",
        "",
        date_label,
        activity_label, 
        distance_miles, 
        duration, 
        avg_pace,
        avg_hr,
        "",
        description
    ]

    safe_request(sheet.insert_row, row, index=insert_index)

    # format new row
    safe_request(set_row_height, sheet, str(insert_index), ROW_HEIGHT) # set row height
    safe_request(sheet.format, f"A{insert_index}:J{insert_index}", {
        "backgroundColor": row_color,
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE",
        "textFormat": {"fontSize": 10}
    })
    safe_request(sheet.format, f"J{insert_index}", {"horizontalAlignment": "LEFT"})



def get_tab_name(workout_date, season_ranges=None):
        if season_ranges:
            # sort seasons
            sorted_seasons = sorted(season_ranges.items(), key=lambda x: x[1], reverse=True)
            for tab_title, start_str in sorted_seasons:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                if workout_date >= start_date:
                    return tab_title
            return "uncategorized" # if not in a range
        else:
            # default to year if no custom tab range
            return str(workout_date.year)


# Convert 1-based column index to A1 notation letter
def col_index_to_letter(index):
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result
    

def set_column_widths(sheet):
    widths = [20, 20, 100, 80, 80, 80, 80, 80, 60, 500]
    for i, w in enumerate(widths, start=1):
        set_column_width(sheet, col_index_to_letter(i), w)


# track start of each week
def get_week_index(workout_date, anchor_date):
    delta_days = (workout_date - anchor_date).days
    return delta_days // 7


def rgb_to_normalized(rgb):
    return {
        "red": rgb[0] / 255,
        "green": rgb[1] / 255,
        "blue": rgb[2] / 255
    }


def sec_to_hms(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h <= 0:
        return f"{int(m):02}:{int(s):02}"
    elif h <= 0 and m <= 0:
        return f"{int(s):02}"
    else:
        return f"{int(h):01}:{int(m):02}:{int(s):02}"


def get_tab_sort_key(tab_title, season_ranges):
    if season_ranges and tab_title in season_ranges:
        return datetime.strptime(season_ranges[tab_title], "%Y-%m-%d")
    try:
        return datetime.strptime(tab_title.split()[-1], "%Y")  # fallback
    except:
        return datetime.min  # push unknowns to the front


# gets the most recent workout date synced
def get_last_workout_date(sheet):
    rows = sheet.get_all_values()
    inferred_year = None
    month_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$")


    for row in reversed(rows):
         # Check for most recent month
        if len(row) >= 1:
            cell = row[0].strip()
            match = month_pattern.match(cell)
            if match:
                _, year = match.groups()
                inferred_year = int(year)

        # get last day/month
        if len(row) < 3:
            continue
        date_str = row[2].strip()  # get date column
        try:
            return datetime.strptime(f"{inferred_year}-{date_str}", "%Y-%m/%d").date()
        except ValueError:
            continue  # skip header, divider, and weird rows
    return None




# gets the first date in the sheet to base the week number off of
def get_first_date(sheet, unsynced_dates):
    rows = sheet.get_all_values()
    inferred_year = None
    month_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$")


    # Go through rows from top to bottom
    for row in rows:
        if len(row) >= 1:
            cell = row[0].strip()
            match = month_pattern.match(cell)
            if match:
                _, year = match.groups()
                inferred_year = int(year)

        if len(row) >= 3:
            date_str = row[2].strip()
            try:
                if inferred_year:
                    return datetime.strptime(f"{inferred_year}-{date_str}", "%Y-%m/%d").date()
            except ValueError:
                continue

    # fallback: no existing date found
    return min(unsynced_dates)







# get month dividers that are already in the sheet
def get_existing_month_dividers(sheet):
    rows = sheet.get_all_values()
    month_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$")
    existing_months = set()

    for row in rows:
        if len(row) >= 1:
            cell = row[0].strip()
            # check if the first col in the row has a month in it
            match = month_pattern.match(cell)
            if match:
                # add to month to existing_months in YYYY-MM format
                month_name, year = match.groups()
                month_num = datetime.strptime(month_name, "%B").month
                existing_months.add(f"{year}-{month_num:02}")
    
    return existing_months


# finds the rows with a given date
def find_rows_with_date(sheet, target_date):
    rows = sheet.get_all_values()
    target_str = target_date.strftime("%m/%d")
    rows_to_delete = []

    for i, row in enumerate(rows, start=1): 
        if len(row) >= 3 and row[2].strip() == target_str:
            rows_to_delete.append(i)

    return rows_to_delete







