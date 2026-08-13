from datetime import datetime
from pathlib import Path


class Logger:

    def __init__(self):

        log_dir = Path("logs")

        log_dir.mkdir(exist_ok=True)

        self.file = log_dir / f"{datetime.now():%Y-%m-%d}.log"

    # -----------------------------------------------------

    def log(self, message):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{timestamp}] {message}"

        print(line)

        with open(
            self.file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(line + "\n")