from __future__ import annotations

from pathlib import Path
import logging
import re
import shutil
import subprocess
import sys
import tempfile

from openpyxl import Workbook

from campx.excel.participant_sheets import (
    fill_schedule_sheet_for_participant,
    make_unique_schedule_sheet_name,
)
from campx.excel.schedule import fill_schedule_sheet
from campx.model.camp import Camp

logger = logging.getLogger(__name__)


def _sanitize_file_component(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", value).strip()
    return cleaned or "output"


def _find_osascript() -> str | None:
    return shutil.which("osascript")


def _apple_script_for_numbers() -> str:
    return """
on run argv
    set inputPath to item 1 of argv
    set outputPath to item 2 of argv

    tell application "Numbers"
        set docRef to open POSIX file inputPath
        export docRef to POSIX file outputPath as PDF
        close docRef saving no
    end tell
end run
""".strip()


def _apple_script_for_excel() -> str:
    return """
on run argv
    set inputPath to item 1 of argv
    set outputPath to item 2 of argv

    tell application "Microsoft Excel"
        set wb to open workbook workbook file name (POSIX file inputPath)
        save workbook as wb filename (POSIX file outputPath) file format PDF file format
        close wb saving no
    end tell
end run
""".strip()


def _convert_xlsx_to_pdf_with_applescript(
    xlsx_path: Path, pdf_path: Path, osascript_path: str
) -> bool:
    app_scripts: list[tuple[str, str]] = [
        ("Microsoft Excel", _apple_script_for_excel()),
        ("Numbers", _apple_script_for_numbers()),
    ]

    for app_name, script in app_scripts:
        command = [
            osascript_path,
            "-e",
            script,
            "--",
            str(xlsx_path),
            str(pdf_path),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            if pdf_path.exists():
                return True
        except subprocess.CalledProcessError as exc:
            logger.debug(
                "AppleScript conversion with %s failed for %s: %s",
                app_name,
                xlsx_path,
                (exc.stderr or "").strip(),
            )

    logger.warning("Failed to convert %s to PDF using AppleScript.", xlsx_path)
    return False


def export_schedule_pdfs(camp: Camp, output_dir: Path | None = None) -> list[Path]:
    """Export schedule PDFs for the main schedule and each leader sheet on macOS."""
    if sys.platform != "darwin":
        logger.warning(
            "Skipping PDF export: AppleScript export is only supported on macOS."
        )
        return []

    osascript_path = _find_osascript()
    if not osascript_path:
        logger.warning("Skipping PDF export: osascript not found.")
        return []

    output_dir = (output_dir or Path()).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    camp_name = _sanitize_file_component(camp.name)
    pdf_paths: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="campx_pdf_") as temp_dir:
        temp_dir_path = Path(temp_dir)

        main_workbook = Workbook()
        main_sheet = main_workbook.active
        main_sheet.title = "Schema"
        fill_schedule_sheet(camp, main_sheet)

        main_xlsx_path = temp_dir_path / f"{camp_name}_Schema.xlsx"
        main_pdf_path = output_dir / f"{camp_name}_Schema.pdf"
        main_workbook.save(main_xlsx_path)
        if _convert_xlsx_to_pdf_with_applescript(
            main_xlsx_path, main_pdf_path, osascript_path
        ):
            pdf_paths.append(main_pdf_path)

        for leader in camp.leaders:
            leader_workbook = Workbook()
            leader_sheet = leader_workbook.active
            leader_sheet.title = make_unique_schedule_sheet_name(
                leader_workbook, leader
            )
            fill_schedule_sheet_for_participant(camp, leader_sheet, leader)

            leader_name = _sanitize_file_component(leader.nick_name or leader.full_name)
            leader_xlsx_path = temp_dir_path / f"{camp_name}_{leader_name}.xlsx"
            leader_pdf_path = output_dir / f"{camp_name}_{leader_name}.pdf"
            leader_workbook.save(leader_xlsx_path)

            if _convert_xlsx_to_pdf_with_applescript(
                leader_xlsx_path, leader_pdf_path, osascript_path
            ):
                pdf_paths.append(leader_pdf_path)

    logger.info("Generated %d schedule PDF files via AppleScript.", len(pdf_paths))
    return pdf_paths
