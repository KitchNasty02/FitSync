import gspread
from gspread_formatting import *
from gspread_formatting import TextFormat, CellFormat, format_cell_range
from collections import defaultdict


def update_header(sheet):
    # Add update for weekly mileage graphs and stuff
    # would shift the frozen rows down

    headers = ["", "Date", "Activity", "Distance", "Time", "Avg HR", "RPE", "Description"]
    sheet.update("A1", [headers])
    set_frozen(sheet, rows=1)


def sync_sheet(sheet, workout_data):

    top_row = sheet.row_values(2)
    latest_date = top_row[1] if len(top_row) > 1 else None

    # existing_values = sheet.get_all_values()
    # existing_dates = [row[1] for row in existing_values[1:] if len(row) > 1]

    # only get workout with newer dates
    unsynced = [
        w for w in workout_data
        if not latest_date or w["date"].isoformat() > latest_date
    ]

    if not unsynced:
        print("Sheet is already up to date.")
        return
    
    
    daily_groups = defaultdict(list)
    for w in unsynced:
        daily_groups[w["date"]].append(w)

    # insert new row at top after header
    insert_index = 2
    last_month = None
    for date in sorted(daily_groups.keys(), reverse=True):
        
        # check month change
        current_month = date.strftime('%Y-%m')
        if current_month != last_month:
            divider_text = date.strftime('%B %Y')
            sheet.insert_row([divider_text], index=insert_index)
            sheet.merge_cells(f"A{insert_index}:H{insert_index}")

            # Apply formatting: bold, left-aligned, gray fill
            sheet.format(f"A{insert_index}:G{insert_index}", {
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                "horizontalAlignment": "LEFT",
                "textFormat": {"fontSize": 10, "bold": True}
            })

            insert_index += 1
            last_month = current_month


        workouts = daily_groups[date]
        start_row = insert_index

        for i, workout in enumerate(workouts):
            row = [
                "",  # Column A blank
                date.isoformat() if i == 0 else "",  # Merge-style visual
                workout.get("name", ""),
                workout.get("type", ""),
                workout.get("duration", ""),
                workout.get("distance", ""),
                workout.get("notes", "")
            ]
            sheet.insert_row(row, index=insert_index)

            # Format newly inserted row
            sheet.format(f"A{insert_index}:G{insert_index}", {
                "backgroundColor": {"red": 1, "green": 1, "blue": 1},
                "textFormat": {"fontSize": 10}
            })

            insert_index += 1

        # Merge date cells across grouped rows
        if len(workouts) > 1:
            sheet.merge_cells(f"B{start_row}:B{insert_index - 1}")


    print(f"Inserted {sum(len(v) for v in daily_groups.values())} new workouts.")












