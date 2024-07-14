import os
import time

def record_message(
        _time: time.struct_time,
        name: str,
        number: int,
        _type: str,
        filename: str = None
) -> None:
    time_str = f"{_time.tm_mday}/{_time.tm_mon}/{_time.tm_year} {_time.tm_hour}:{_time.tm_min}"

    if not os.path.exists("AutoWA_history.txt"):
        file = open("AutoWA_history.txt", "w+")
        file.close()
    
    with open("AutoWA_history.txt", "a", encoding="utf-8") as file:
        if _type == "file":
            file.write(
                f"{time_str}: {filename} has been successfully sent to {number} ({name})\n"
            )
        else:
             file.write(
                f"{time_str}: message has been successfully sent to {number} ({name})\n"
            )

        file.close()