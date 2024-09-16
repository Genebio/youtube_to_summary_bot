# utils/datetime_utils.py
from datetime import datetime
from config.config import ARMENIA_TZ, DATETIME_FORMAT

def get_formatted_time():
    """Returns the current time in Armenia formatted as 'day-month-year hour:min:sec'."""
    armenian_time = datetime.now(ARMENIA_TZ)
    return armenian_time.strftime(DATETIME_FORMAT)