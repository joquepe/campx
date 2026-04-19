from pathlib import Path

from campx.repository import Repository
from campx.factory import Factory
from campx.excel.excel_generation import create_camp_excel
from campx.validation import run_validations
from campx.icalendar.generate import create_calendar


def main(camp_name: str, input_dir: Path | None = None, validate: bool = True) -> None:
    """Generate Excel and calendar output for a named camp."""
    factory = Factory(input_base_dir=input_dir)
    repository = Repository(factory)
    camp = repository.get_camp(camp_name)

    if validate:
        run_validations(camp)

    create_camp_excel(camp)
    create_calendar(camp)
