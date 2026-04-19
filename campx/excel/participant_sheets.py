from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.properties import PageSetupProperties, WorksheetProperties
from openpyxl.utils import get_column_letter
from campx.model.camp import Camp
from campx.excel.utilities import Colors

INVALID_SHEET_CHARS = set("[]:*?/\\")
MAX_SHEET_NAME_LENGTH = 31


def _setup_worksheet(ws: Worksheet):
    ws.page_setup.paperSize = 9  # A4
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToHeight = 1
    ws.page_setup.fitToWidth = 0
    ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.75, bottom=0.75)
    ws.print_options.gridLines = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties = WorksheetProperties(
        pageSetUpPr=PageSetupProperties(fitToPage=True)
    )


def _sanitize_sheet_name(name: str) -> str:
    cleaned = "".join(ch for ch in name if ch not in INVALID_SHEET_CHARS)
    cleaned = cleaned.strip()
    if len(cleaned) > MAX_SHEET_NAME_LENGTH:
        cleaned = cleaned[:MAX_SHEET_NAME_LENGTH]
    return cleaned or "Participant"


def _make_unique_sheet_name(workbook, base_name: str) -> str:
    base_name = _sanitize_sheet_name(base_name)
    if base_name not in workbook.sheetnames:
        return base_name

    suffix = 1
    while True:
        suffix_name = (
            f"{base_name[: MAX_SHEET_NAME_LENGTH - len(str(suffix)) - 1]}_{suffix}"
        )
        if suffix_name not in workbook.sheetnames:
            return suffix_name
        suffix += 1


def _write_table_headers(
    ws: Worksheet, start_row: int, start_col: int, headers: list[str]
):
    for offset, header in enumerate(headers):
        cell = ws.cell(row=start_row, column=start_col + offset, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            bottom=Side(style="thin", color=Colors.BLACK),
            right=Side(style="thin", color=Colors.BLACK),
        )


def _auto_adjust_column_widths(ws: Worksheet):
    for col_idx in range(1, ws.max_column + 1):
        max_len = max(
            (
                len(str(ws.cell(row=row, column=col_idx).value or ""))
                for row in range(1, ws.max_row + 1)
            ),
            default=0,
        )
        ws.column_dimensions[get_column_letter(col_idx)].width = max(10, max_len + 2)


def fill_participant_sheet(camp: Camp, ws: Worksheet, participant):
    _setup_worksheet(ws)

    nickname = participant.nick_name or participant.full_name
    sheet_title = nickname

    title = ws.cell(row=1, column=1, value="Participant schedule")
    title.font = Font(bold=True, size=14)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

    ws.cell(row=2, column=1, value="Name:")
    ws.cell(row=2, column=1).font = Font(bold=True)
    ws.cell(row=2, column=2, value=participant.full_name)
    ws.cell(row=2, column=2).alignment = Alignment(vertical="center", horizontal="left")

    ws.cell(row=3, column=1, value="Nickname:")
    ws.cell(row=3, column=1).font = Font(bold=True)
    nickname_cell = ws.cell(row=3, column=2, value=nickname)
    nickname_cell.font = Font(bold=True, color="FF0000")
    nickname_cell.alignment = Alignment(vertical="center", horizontal="left")

    headers = ["Day", "Entry type", "Entry name", "Start", "End", "Responsible"]
    start_row = 5
    _write_table_headers(ws, start_row, 1, headers)

    row = start_row + 1
    for day in camp.schedule.days:
        for entry in day.schedule_entries:
            responsible_names = [
                leader.nick_name or leader.initials for leader in entry.responsible
            ]
            responsible_text = ", ".join(responsible_names)
            is_target_responsible = participant in entry.responsible

            ws.cell(row=row, column=1, value=day.as_str())
            ws.cell(row=row, column=2, value=entry.entry_type.value.short)
            ws.cell(row=row, column=3, value=entry.name or entry.entry_type.value.long)
            ws.cell(row=row, column=4, value=entry.start_time or "")
            ws.cell(row=row, column=5, value=entry.end_time or "")
            ws.cell(row=row, column=6, value=responsible_text)

            if is_target_responsible:
                fill = PatternFill(
                    start_color="FFCCCC", end_color="FFCCCC", fill_type="solid"
                )
                for col in range(1, 7):
                    ws.cell(row=row, column=col).fill = fill

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = Border(
                    bottom=Side(style="thin", color=Colors.BLACK),
                    right=Side(style="thin", color=Colors.BLACK),
                )
            row += 1

    _auto_adjust_column_widths(ws)

    return _make_unique_sheet_name(ws.parent, sheet_title)


def add_participant_sheets(camp: Camp, workbook):
    for participant in camp.participants:
        sheet_name = participant.nick_name or participant.full_name
        sheet_name = _make_unique_sheet_name(workbook, sheet_name)
        participant_sheet = workbook.create_sheet(title=sheet_name)
        fill_participant_sheet(camp, participant_sheet, participant)
