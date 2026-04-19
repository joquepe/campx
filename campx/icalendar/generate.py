from ics import Calendar, Event
from campx.model.camp import Camp
import datetime as dt
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)


ZONE = "Europe/Stockholm"


def create_calendar(camp: Camp):
    logger.info("Generating .ics file...")
    calendar = Calendar()
    for day in camp.schedule.days:
        for entry in day.schedule_entries:
            event = Event()
            event.name = entry.entry_type.value.emoji
            if isinstance(entry.name, str):
                event.name += entry.name
            else:
                event.name += entry.entry_type.value.long

            event.location = ", ".join(r.initials for r in entry.responsible)
            event.description = ", ".join(r.full_name for r in entry.responsible)

            if entry.start_time is None:
                event.begin = dt.date(day.date.year, day.date.month, day.date.day)
                event.make_all_day()
            else:
                start_hour = int(entry.start_time.split(":")[0])
                start_minute = int(entry.start_time.split(":")[1])
                start = dt.datetime(
                    day.date.year,
                    day.date.month,
                    day.date.day,
                    start_hour,
                    start_minute,
                    tzinfo=ZoneInfo(ZONE),
                )
                end_hour = int(entry.end_time.split(":")[0])
                end_minute = int(entry.end_time.split(":")[1])
                end = dt.datetime(
                    day.date.year,
                    day.date.month,
                    day.date.day,
                    end_hour,
                    end_minute,
                    tzinfo=ZoneInfo(ZONE),
                )
                event.begin = start
                event.end = end

            calendar.events.add(event)

    with open(f"{camp.name}.ics", "w") as f:
        f.writelines(calendar)

    logger.info(f"Created ics file at {camp.name}.ics")
