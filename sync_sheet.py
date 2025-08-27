from gspread_formatting import set_frozen, set_column_width
from collections import defaultdict
from datetime import datetime
import time


# ensures the api request do not fail from the rate limit
def safe_request(func, *args, max_sleep=60, **kwargs):
    for sleep_time in [1, 2, 4, 8, 16, 32, max_sleep]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit hit, trying again in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise e


# colors
MONTH_COLOR = (207, 226, 243)
HEADERS_COLOR = (159, 197, 232)
ROW_COLORS = [
    {"red": 0.95, "green": 0.95, "blue": 0.95},  # medium gray
    {"red": 1.0,  "green": 1.0,  "blue": 1.0}    # white
]

# convert to better labels in sheet
TYPEKEY_MAP = {
    "running": "Run",
    "cycling": "Bike",
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

    headers = ["", "Date", "Activity", "Distance", "Time", "Avg HR", "RPE", "Description"]
    safe_request(sheet.update, "A1", [headers])
    safe_request(sheet.format, "A1:H1", {
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
        
    def col_index_to_letter(index):
        # Convert 1-based column index to A1 notation letter
        result = ""
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = chr(65 + remainder) + result
        return result
        
    def set_column_widths(sheet):
        widths = [20, 100, 80, 80, 80, 80, 60, 200]
        for i, w in enumerate(widths, start=1):
            set_column_width(sheet, col_index_to_letter(i), w)
    

    # group workouts by tab
    tab_groups = defaultdict(lambda: defaultdict(list)) # {tab_title: {date: [workouts]}}

    for w in workout_data:
        if isinstance(w["startTimeLocal"], str):
            w["startTimeLocal"] = datetime.strptime(w["startTimeLocal"], "%Y-%m-%d %H:%M:%S")
        
        workout_date = w["startTimeLocal"].date()
        tab_title = get_tab_name(workout_date, season_ranges)
        tab_groups[tab_title][workout_date].append(w)
    
    for tab_title, daily_groups in tab_groups.items():
        # get or create tab
        if tab_title not in tab_map:
            try:
                tab_map[tab_title] = spreadsheet.worksheet(tab_title)
            except:
                # TODO: update these to set up right number of rows/cols
                tab_map[tab_title] = spreadsheet.add_worksheet(title=tab_title, rows=20, cols=8)
                update_header(tab_map[tab_title])
                set_column_widths(tab_map[tab_title])

        sheet = tab_map[tab_title]

        top_row = sheet.row_values(3)
        latest_date = top_row[1] if len(top_row) > 1 else None

        unsynced_dates = [
            date for date in daily_groups
            if not latest_date or date.strftime("%m/%d") > latest_date
        ]
        if not unsynced_dates:
            print(f"Tab '{tab_title}' is already up to date.")
            continue


        # insert workouts

        insert_index = 2
        last_month = None
        color_index = 0

        for date in sorted(daily_groups.keys(), reverse=True):
            # check month change
            current_month = date.strftime('%Y-%m')
            if current_month != last_month:
                insert_month_divider(sheet, date, insert_index)
                insert_index += 1
                last_month = current_month


            workouts = daily_groups[date]
            start_row = insert_index
            group_color = ROW_COLORS[color_index]

            for i, workout in enumerate(workouts):
                insert_row(sheet, workout, date, insert_index, i == 0, row_color=group_color)
                insert_index += 1

            # Merge date cells across grouped rows
            if len(workouts) > 1:
                safe_request(sheet.merge_cells, f"B{start_row}:B{insert_index - 1}")
                safe_request(sheet.format, f"B{start_row}", {"verticalAlignment": "MIDDLE"})

            color_index = 1 - color_index

        print(f"Inserted {sum(len(v) for v in daily_groups.values())} new workouts into '{tab_title}'")



def insert_month_divider(sheet, date, insert_index):
    divider_text = date.strftime('%B %Y')
    
    safe_request(sheet.insert_row, [divider_text], index=insert_index)
    safe_request(sheet.merge_cells, f"A{insert_index}:H{insert_index}")

    safe_request(sheet.format, f"A{insert_index}:G{insert_index}", {
        "backgroundColor": rgb_to_normalized(MONTH_COLOR),
        "horizontalAlignment": "LEFT",
        "textFormat": {"fontSize": 10, "bold": True}
    })



def insert_row(sheet, workout, date, insert_index, is_first_row, row_color):
    
    raw_type = workout.get("activityType", {}).get("typeKey", "")
    activity_label = TYPEKEY_MAP.get(raw_type, raw_type.title())

    row = [
        "",
        date.strftime('%m/%d') if is_first_row else "",  
        activity_label, 
        round(workout.get("distance", 0) / 1609.34, 2), 
        sec_to_hms(workout.get("duration", 0)), 
        workout.get("averageHR", ""),
        "",
        workout.get("description", "")
    ]

    safe_request(sheet.insert_row, row, index=insert_index)

    # format new row
    safe_request(sheet.format, f"A{insert_index}:H{insert_index}", {
        "backgroundColor": row_color,
        "horizontalAlignment": "CENTER",
        "textFormat": {"fontSize": 10}
    })
    safe_request(sheet.format, f"H{insert_index}", {"horizontalAlignment": "LEFT"})




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







