from datetime import datetime, timezone
import time

def get_current_timestamp() -> int:
    """
    Returns the current time as a Unix timestamp (seconds since the epoch).
    """
    return int(time.time())

def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Converts a Unix timestamp to a datetime object in UTC.
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def datetime_to_timestamp(dt: datetime) -> int:
    """
    Converts a datetime object to a Unix timestamp.
    """
    return int(dt.timestamp())

def format_timestamp_for_display(timestamp: int) -> str:
    """
    Formats a Unix timestamp as a string for display purposes.
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%d-%m-%Y %H:%M:%S')