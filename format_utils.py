import gspread
from gspread_formatting import *
from gspread_formatting import TextFormat, CellFormat, format_cell_range


def format_sheet(sheet):
    # Headers
    headers = ["Weekly Mileage", "Date", "Daily Mileage", "RPE", "Description", 
               "Duration (min)", "Avg HR", "Swim (km)", "Swim (min)", "Bike (km)", "Bike (min)", "Extra"]
    sheet.update('A1', [headers])
    set_frozen(sheet, rows=1)

    # Column widths
    widths = [130, 90, 110, 60, 200, 120, 90, 90, 90, 90, 90]
    for i, width in enumerate(widths, start=1):
        col_letter = col_index_to_letter(i)
        set_column_width(sheet, col_letter, width)

    # Bold and shade header
    # header_fmt = CellFormat(
    #     textFormat=TextFormat(bold=True),
    #     backgroundColor=Color(0.85, 0.85, 0.85)
    # )
    # format_cell_range(sheet, "A1:K1", header_fmt)

    set_font_and_size(sheet)

    # Alternating week colors: loop in 7-row blocks
    for start_row in range(2, 200, 7):
        end_row = start_row + 6
        week_range = f"A{start_row}:K{end_row}"
        bg_color = Color(0.97, 0.97, 1.0) if (start_row // 7) % 2 == 0 else Color(0.95, 0.95, 0.95)
        format_cell_range(sheet, week_range, CellFormat(backgroundColor=bg_color))



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

