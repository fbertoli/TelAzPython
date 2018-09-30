from difflib import SequenceMatcher
import sys

days_map = {"lun": 0, "mar": 1, "mer": 2, "gio": 3, "ven": 4, "sab": 5, "dom": 6, \
            "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


# -- put year in format 20XX
def format_year(x):
    return int(x) + (2000 if int(x) < 100 else 0)


# -- parse a string hh:mm in int hour and minute with the convention 24:00 -> h = 23, m = 59 and
def get_hour_minute(x):
    hour, minute = [int(item) for item in x.strip().split(":")]
    if hour == 24 and minute == 0:
        return 23, 59
    elif hour == 0 and minute == 0:
        return 0, 1
    else:
        return int(hour), int(minute)


# -- find similarity between two string
def similar_string(string1, string2):
    return SequenceMatcher(None, string1, string2).ratio()


# -- safety check, same thing as assert
def safety_check(condition, string=""):
    if not condition:
        sys.exit(string)


# -- determine if shift is a night shift (end is integer represeting hours)
def is_night_shift(name, end):
    return end < 9
