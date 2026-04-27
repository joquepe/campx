import datetime as dt

from campx.model.enums import EntryType


DEFAULT_VALIDATION_CONFIG = {
    "leader_limits": {
        "overlap_rules": (
            (EntryType.SLEEP_IN, EntryType.WAKE_UP, 0, 0),
            (EntryType.SLEEP_IN, EntryType.MORNING_PRAYER, 0, 0),
            (EntryType.WAKE_UP, EntryType.MORNING_PRAYER, 0, 0),
            (EntryType.EVENING_PRAYER, EntryType.PUT_TO_BED, 0, 0),
            (EntryType.EVENING_PRAYER, EntryType.EVENING_ACTIVITY, 0, 0),
            (EntryType.PUT_TO_BED, EntryType.WAKE_UP, 0, 0),
            (EntryType.PUT_TO_BED, EntryType.WAKE_UP, 1, 0),
            (EntryType.PUT_TO_BED, EntryType.MORNING_PRAYER, 1, 0),
            (EntryType.DAY_OFF, EntryType.WAKE_UP, 1, 0),
            (EntryType.PUT_TO_BED, EntryType.DAY_OFF, 1, 0),
            (EntryType.WAKE_UP, EntryType.WAKE_UP, 1, 0),
            (EntryType.EVENING_PRAYER, EntryType.DAY_OFF, 1, 0),
            (EntryType.EVENING_PRAYER, EntryType.MORNING_PRAYER, 1, 0),
        ),
        "max_responsibilities_per_day": 3,
        "max_responsibilities_per_entry_type": (
            (EntryType.EVENING_ACTIVITY, 3),
            (EntryType.MORNING_PRAYER, 2),
            (EntryType.EVENING_PRAYER, 2),
            (EntryType.AFTERNOON_ACTIVITY, 2),
            (EntryType.WAKE_UP, 3),
            (EntryType.PUT_TO_BED, 3),
            (EntryType.DAY_OFF, 1),
            (EntryType.DAY_HOST, 2),
            (EntryType.SLEEP_IN, 2),
            ((EntryType.WAKE_UP, EntryType.PUT_TO_BED), 5),
            (
                (
                    EntryType.EVENING_ACTIVITY,
                    EntryType.MORNING_PRAYER,
                    EntryType.EVENING_PRAYER,
                    EntryType.AFTERNOON_ACTIVITY,
                ),
                6,
            ),
        ),
        "min_responsibilities_per_entry_type": {
            EntryType.SLEEP_IN: 2,
            EntryType.DAY_OFF: 1,
        },
        "min_days_between_entry_types": ((EntryType.DAY_OFF, EntryType.SLEEP_IN, 2),),
    },
    "entry_limits": {
        "max_responsible_per_entry_type": {
            EntryType.EDUCATION: 3,
            EntryType.FEEDBACK: 3,
            EntryType.EVENING_ACTIVITY: 4,
            EntryType.AFTERNOON_ACTIVITY: 4,
            EntryType.MORNING_PRAYER: 3,
            EntryType.EVENING_PRAYER: 3,
            EntryType.WAKE_UP: 4,
            EntryType.PUT_TO_BED: 4,
            EntryType.SLEEP_IN: 4,
            EntryType.DAY_OFF: 5,
            EntryType.BOAT: 4,
            EntryType.DAY_HOST: 4,
        },
        "min_responsible_per_entry_type": {
            EntryType.MORNING_PRAYER: 2,
            EntryType.EVENING_PRAYER: 2,
            EntryType.WAKE_UP: 4,
            EntryType.PUT_TO_BED: 4,
            EntryType.EVENING_ACTIVITY: 2,
        },
    },
}

CAMP_CONFIGS = {
    "Karlberg 5 2025": {
        "camp_place_name": "Karlberg",
        "start_date": dt.date(2025, 7, 30),
        "end_date": dt.date(2025, 8, 11),
        "schedule_config_id": 1,
    },
    "Karlberg 3 2026": {
        "camp_place_name": "Karlberg",
        "start_date": dt.date(2026, 7, 6),
        "end_date": dt.date(2026, 7, 18),
        "schedule_config_id": 1,
    },
    "Karlberg 4 2026": {
        "camp_place_name": "Karlberg",
        "start_date": dt.date(2026, 7, 18),
        "end_date": dt.date(2026, 7, 30),
        "schedule_config_id": 1,
        "validation_overrides": {
            "leader_limits": {
                "min_responsibilities_per_entry_type": {
                    EntryType.SLEEP_IN: 1,
                },
            },
            "entry_limits": {
                "max_responsible_per_entry_type": {
                    EntryType.DAY_OFF: 8,
                    EntryType.SLEEP_IN: 5,
                },
            },
        },
    },
}


def get_camp_config(camp_name: str):
    return CAMP_CONFIGS[camp_name]


def get_validation_config(camp_name: str) -> dict:
    camp_config = CAMP_CONFIGS.get(camp_name, {})
    validation_overrides = camp_config.get("validation_overrides", {})
    leader_overrides = validation_overrides.get("leader_limits", {})
    entry_overrides = validation_overrides.get("entry_limits", {})

    return {
        "leader_limits": {
            "overlap_rules": leader_overrides.get(
                "overlap_rules",
                DEFAULT_VALIDATION_CONFIG["leader_limits"]["overlap_rules"],
            ),
            "max_responsibilities_per_day": leader_overrides.get(
                "max_responsibilities_per_day",
                DEFAULT_VALIDATION_CONFIG["leader_limits"][
                    "max_responsibilities_per_day"
                ],
            ),
            "max_responsibilities_per_entry_type": leader_overrides.get(
                "max_responsibilities_per_entry_type",
                DEFAULT_VALIDATION_CONFIG["leader_limits"][
                    "max_responsibilities_per_entry_type"
                ],
            ),
            "min_responsibilities_per_entry_type": DEFAULT_VALIDATION_CONFIG[
                "leader_limits"
            ]["min_responsibilities_per_entry_type"]
            | leader_overrides.get("min_responsibilities_per_entry_type", {}),
            "min_days_between_entry_types": leader_overrides.get(
                "min_days_between_entry_types",
                DEFAULT_VALIDATION_CONFIG["leader_limits"][
                    "min_days_between_entry_types"
                ],
            ),
        },
        "entry_limits": {
            "max_responsible_per_entry_type": DEFAULT_VALIDATION_CONFIG["entry_limits"][
                "max_responsible_per_entry_type"
            ]
            | entry_overrides.get("max_responsible_per_entry_type", {}),
            "min_responsible_per_entry_type": entry_overrides.get(
                "min_responsible_per_entry_type",
                DEFAULT_VALIDATION_CONFIG["entry_limits"][
                    "min_responsible_per_entry_type"
                ],
            ),
        },
    }
