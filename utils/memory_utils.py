import psutil


def get_current_ram_usage() -> int:
    """
    Get current RAM usage in MB as an integer (whole number).
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    return int(mem_info.rss / (1024 * 1024))  # Convert from bytes to MB and return as an integer

def get_free_ram_left() -> int:
    """
    Get the amount of free RAM left in MB as an integer (whole number).
    """
    mem_info = psutil.virtual_memory()
    return int(mem_info.available / (1024 * 1024))  # Convert from bytes to MB and return as an integer