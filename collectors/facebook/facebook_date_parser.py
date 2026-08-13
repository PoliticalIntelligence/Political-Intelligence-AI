from datetime import datetime, timedelta
import re


class FacebookDateParser:
    """
    Converts Facebook timestamps into Python datetime objects.

    Supported formats:

    5m
    30m

    2h
    18h

    3d
    45d

    Yesterday

    Monday

    June 20
    June 20 at 8:35 PM
    June 20 at 20:35

    Jul 4
    Jul 4 at 9:15 AM

    20 June
    20 June at 8:35 PM
    20 June at 20:35

    20 Jul
    20 Jul at 7:08
    """

    def __init__(self):

        self.now = datetime.now()

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def parse(self, text: str):

        if not text:
            return None

        text = text.strip()

        parsers = [

            self.minutes,

            self.hours,

            self.days,

            self.yesterday,

            self.weekday,

            self.month_day,

        ]

        for parser in parsers:

            try:

                result = parser(text)

                if result:

                    return result

            except Exception:

                pass

        return None

    # ---------------------------------------------------------
    # 5m
    # ---------------------------------------------------------

    def minutes(self, text):

        m = re.fullmatch(r"(\d+)\s*m", text)

        if not m:
            return None

        return self.now - timedelta(minutes=int(m.group(1)))

    # ---------------------------------------------------------
    # 3h
    # ---------------------------------------------------------

    def hours(self, text):

        m = re.fullmatch(r"(\d+)\s*h", text)

        if not m:
            return None

        return self.now - timedelta(hours=int(m.group(1)))

    # ---------------------------------------------------------
    # 5d
    # ---------------------------------------------------------

    def days(self, text):

        m = re.fullmatch(r"(\d+)\s*d", text)

        if not m:
            return None

        return self.now - timedelta(days=int(m.group(1)))

    # ---------------------------------------------------------
    # Yesterday
    # ---------------------------------------------------------

    def yesterday(self, text):

        if text.lower() != "yesterday":
            return None

        return self.now - timedelta(days=1)

    # ---------------------------------------------------------
    # Monday
    # ---------------------------------------------------------

    def weekday(self, text):

        weekdays = [

            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday"

        ]

        lower = text.lower()

        if lower not in weekdays:
            return None

        target = weekdays.index(lower)

        today = self.now.weekday()

        diff = (today - target) % 7

        if diff == 0:
            diff = 7

        return self.now - timedelta(days=diff)

    # ---------------------------------------------------------
    # Month / Day parser
    # ---------------------------------------------------------

    def month_day(self, text):

        current_year = self.now.year

        patterns = [

            # Month Day

            "%B %d",
            "%b %d",

            "%B %d at %I:%M %p",
            "%b %d at %I:%M %p",

            "%B %d at %H:%M",
            "%b %d at %H:%M",

            # Day Month

            "%d %B",
            "%d %b",

            "%d %B at %I:%M %p",
            "%d %b at %I:%M %p",

            "%d %B at %H:%M",
            "%d %b at %H:%M",

        ]

        for fmt in patterns:

            try:

                dt = datetime.strptime(text, fmt)

                dt = dt.replace(year=current_year)

                if dt > self.now:

                    dt = dt.replace(year=current_year - 1)

                return dt

            except Exception:

                pass

        return None

    # ---------------------------------------------------------
    # Within N days
    # ---------------------------------------------------------

    def within_days(self, text, days):

        dt = self.parse(text)

        if dt is None:

            return False

        return (self.now - dt).days <= days