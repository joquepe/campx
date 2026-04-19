from campx.model.enums import EntryType

DEFAULT_DAY_SCHEDULES = {
    1: [
        (EntryType.WAKE_UP, "08:00", "08:15"),
        (EntryType.BREAKFAST, "08:15", "09:00"),
        (EntryType.MORNING_PRAYER, "09:00", "09:30"),
        (EntryType.EDUCATION, "09:30", "12:30"),
        (EntryType.LUNCH, "12:30", "13:15"),
        (EntryType.LEADER_MEETING, "13:15", "14:00"),
        (EntryType.AFTERNOON_ACTIVITY, "14:00", "16:30"),
        (EntryType.BOAT, "14:00", "16:30"),
        (EntryType.CLEANING, "17:00", "17:30"),
        (EntryType.DINNER, "17:30", "18:30"),
        (EntryType.FEEDBACK, "18:30", "19:30"),
        (EntryType.EVENING_ACTIVITY, "19:30", "21:00"),
        (EntryType.EVENING_MEAL, "21:00", "21:30"),
        (EntryType.EVENING_PRAYER, "21:30", "22:30"),
        (EntryType.PUT_TO_BED, "22:30", "23:00"),
    ]
}


def get_schedule_config(schedule_config_id: int):
    return DEFAULT_DAY_SCHEDULES[schedule_config_id]
