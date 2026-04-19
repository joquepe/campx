from campx.main import main
from campx.factory import Factory


import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    factory = Factory(input_base_dir=None)
    # factory.create_schedule_template_files("Karlberg 3 2026")
    for camp_name in ["Karlberg 3 2026", "Karlberg 4 2026"]:
        logger.info(f"Processing camp: {camp_name}")
        main(camp_name, None, validate=False)
