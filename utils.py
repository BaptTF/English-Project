import time

def format_time(duration_seconds: float) -> str:
    """
    Format the duration in seconds as a string in the format "H:MM:SS".
    """
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((duration_seconds % 1) * 1000)

    if hours > 0:
        formatted_time = f"{int(hours)}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03d}"
    elif minutes > 0:
        formatted_time = f"{int(minutes)}:{int(seconds):02}.{milliseconds:03d}"
    else:
        formatted_time = f"{int(seconds)}.{milliseconds:03d}"
    return formatted_time