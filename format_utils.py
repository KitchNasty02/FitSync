import gspread
from gspread_formatting import *
from gspread_formatting import TextFormat, CellFormat, format_cell_range






def format_sheet(sheet, workout_data):
    """
    workout_data: list of dicts with keys like
    {
        'date': datetime.date,
        'activity': 'Run',
        'distance': 5.0,
        'time': 30,
        'hr': 135,
        'rpe': 6,
        'description': 'Tempo run'
    }
    """
    from collections import defaultdict
    from gspread_formatting import format_cell_range, CellFormat, Color, TextFormat

    reset_sheet(sheet)
    headers = ["", "Date", "Activity", "Distance", "Time", "Avg HR", "RPE", "Description"]
    sheet.update("A1", [headers])
    set_frozen(sheet, rows=1)
    
    row = 2    # start row for data

    # Sort workouts: most recent month first, then ascending by date
    workout_data.sort(key=lambda w: w['date'], reverse=False)

    # row = 1
    month_groups = defaultdict(list)
    for workout in workout_data:
        month_str = workout['date'].strftime('%B %Y')
        month_groups[month_str].append(workout)

    for month in sorted(month_groups.keys(), reverse=False):
        # Insert month divider
        sheet.update(f"A{row}", [[month]])
        format_cell_range(sheet, f"A{row}:G{row}", CellFormat(
            backgroundColor=Color(0.85, 0.85, 0.85),
            textFormat=TextFormat(bold=True)
        ))
        row += 1

        # Group by date
        daily_groups = defaultdict(list)
        for workout in month_groups[month]:
            daily_groups[workout['date']].append(workout)

        for date, activities in sorted(daily_groups.items(), reverse=True):
            start_row = row
            for workout in activities:
                sheet.update(f"A{row}", [[""]])  # Empty first column
                sheet.update(f"B{row}:H{row}", [[
                    date.strftime('%Y-%m-%d') if row == start_row else "",  # will be merged
                    workout['activity'],
                    workout['distance'],
                    workout['time'],
                    workout['hr'],
                    workout['rpe'],
                    workout['description']
                ]])
                row += 1

            # Merge date column vertically ERROR HERE
            sheet.merge_cells(f"B{start_row}:B{row - 1}")

    # Optional: Column widths
    widths = [20, 100, 80, 80, 80, 80, 60, 200]
    for i, w in enumerate(widths, start=1):
        set_column_width(sheet, col_index_to_letter(i), w)


def col_index_to_letter(index):
    """Convert 1-based column index to A1 notation letter"""
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result



def set_font_and_size(sheet):
    # Set global font and size for all cells (excluding header if you want different style there)
    body_format = CellFormat(
        textFormat=TextFormat(fontFamily='Times New Roman', fontSize=11)
    )
    row_count = len(sheet.get_all_values())
    format_cell_range(sheet, f'A2:Z{row_count}', body_format)

    # format_cell_range(sheet, 'A2:K1000', body_format)

    # Optional: distinct header style
    header_format = CellFormat(
        textFormat=TextFormat(fontFamily='Times New Roman', fontSize=11, bold=True),
        backgroundColor=Color(0.85, 0.85, 0.85)
    )
    format_cell_range(sheet, 'A1:K1', header_format)



def reset_sheet(sheet):
    sheet.clear()

    data = sheet.get_all_values()
    row_count = len(data)
    col_count = max((len(row) for row in data), default=0)

    # unmerge
    sheet.spreadsheet.batch_update({
        "requests": [{
            "unmergeCells": {
                "range": {
                    "sheetId": sheet._properties['sheetId'],
                    "startRowIndex": 0,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": col_count
                }
            }
        }]
    })

    # 4. Clear formatting
    end_cell = gspread.utils.rowcol_to_a1(row_count, col_count)
    range_str = f"A1:{end_cell}"

    format_cell_range(sheet, range_str, CellFormat())

    # 5. Reset frozen panes
    set_frozen(sheet, rows=0, cols=0)



from gspread_formatting import format_cell_range, CellFormat
import gspread.utils

def clear_all_formatting(sheet):
    data = sheet.get_all_values()
    row_count = len(data)
    col_count = max((len(row) for row in data), default=0)

    end_cell = gspread.utils.rowcol_to_a1(row_count, col_count)
    range_str = f"A1:{end_cell}"

    format_cell_range(sheet, range_str, CellFormat())
