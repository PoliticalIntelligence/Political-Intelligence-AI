import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

SPREADSHEET_ID = os.getenv(
    "GOOGLE_SHEETS_ID",
    "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI",
)

# This is the TAB inside "Political Intelligence Database"
SHEET_NAME = os.getenv(
    "AI_ANALYSIS_SHEET",
    "AI Analysis",
)

CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "credentials/service_account.json",
)

OUTPUT_FILE = Path(
    os.getenv(
        "DASHBOARD_DATA_FILE",
        "dashboard/data/dashboard-data.json",
    )
)

IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# BASIC HELPER
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# PARSE SCRAPED AT
# ============================================================

def parse_scraped_at(value):
    raw = clean(value)

    if not raw:
        return None

    # ISO timestamp
    try:
        dt = datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        )

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)

        return dt.astimezone(IST)

    except ValueError:
        pass

    # Other possible formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(
                raw,
                fmt,
            )

            return dt.replace(
                tzinfo=IST
            )

        except ValueError:
            pass

    return None


# ============================================================
# MONTH MAP
# ============================================================

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


# ============================================================
# DATE WITHOUT YEAR
# ============================================================

def parse_day_month_without_year(
    value,
    reference_date,
):
    """
    Handles:
        5 August
        5 Aug
        August 5
        Aug 5
        June 20
        June 20 at 8:35 PM
    """

    raw = clean(value)

    if not raw:
        return None

    # Remove time portion
    raw = re.split(
        r"\s+at\s+",
        raw,
        flags=re.IGNORECASE,
    )[0].strip()

    # Remove commas
    raw = raw.replace(",", " ")

    # Normalize spaces
    raw = re.sub(
        r"\s+",
        " ",
        raw,
    ).strip()

    # --------------------------------------------------------
    # 5 August
    # --------------------------------------------------------

    match = re.match(
        r"^(\d{1,2})\s+([A-Za-z]+)$",
        raw,
    )

    if match:

        day = int(
            match.group(1)
        )

        month_name = (
            match.group(2).lower()
        )

        month = MONTHS.get(
            month_name
        )

        if month:

            return infer_year(
                day,
                month,
                reference_date,
            )

    # --------------------------------------------------------
    # August 5
    # --------------------------------------------------------

    match = re.match(
        r"^([A-Za-z]+)\s+(\d{1,2})$",
        raw,
    )

    if match:

        month_name = (
            match.group(1).lower()
        )

        day = int(
            match.group(2)
        )

        month = MONTHS.get(
            month_name
        )

        if month:

            return infer_year(
                day,
                month,
                reference_date,
            )

    return None


# ============================================================
# INFER YEAR
# ============================================================

def infer_year(
    day,
    month,
    reference_date,
):
    """
    Example:

    Reference: 20 August 2026
    5 August  -> 5 August 2026

    Reference: 10 January 2026
    20 December -> 20 December 2025
    """

    candidates = []

    for year in (
        reference_date.year - 1,
        reference_date.year,
        reference_date.year + 1,
    ):

        try:
            candidate = datetime(
                year,
                month,
                day,
                tzinfo=IST,
            )

            candidates.append(candidate)

        except ValueError:
            continue

    if not candidates:
        return None

    # Prefer the latest date that is not
    # after the reference date.
    past_dates = [
        dt
        for dt in candidates
        if dt.date() <= reference_date.date()
    ]

    if past_dates:
        return max(past_dates)

    # Fallback: closest date
    return min(
        candidates,
        key=lambda dt: abs(
            (dt - reference_date).total_seconds()
        ),
    )


# ============================================================
# RELATIVE FACEBOOK TIMESTAMP
# ============================================================

def parse_relative_timestamp(
    value,
    reference_date,
):
    """
    Handles:

        4h
        30m
        2d
        3d
        2 weeks
        1 month
        yesterday
        today
    """

    raw = clean(value).lower()

    if not raw:
        return None

    raw = raw.replace(
        "ago",
        "",
    ).strip()

    # --------------------------------------------------------
    # HOURS
    # --------------------------------------------------------

    match = re.match(
        r"^(\d+)\s*h$",
        raw,
    )

    if match:

        hours = int(
            match.group(1)
        )

        return reference_date - timedelta(
            hours=hours
        )

    # --------------------------------------------------------
    # MINUTES
    # --------------------------------------------------------

    match = re.match(
        r"^(\d+)\s*m$",
        raw,
    )

    if match:

        minutes = int(
            match.group(1)
        )

        return reference_date - timedelta(
            minutes=minutes
        )

    # --------------------------------------------------------
    # DAYS
    # --------------------------------------------------------

    match = re.match(
        r"^(\d+)\s*d$",
        raw,
    )

    if match:

        days = int(
            match.group(1)
        )

        return reference_date - timedelta(
            days=days
        )

    # --------------------------------------------------------
    # WEEKS
    # --------------------------------------------------------

    match = re.match(
        r"^(\d+)\s*weeks?$",
        raw,
    )

    if match:

        weeks = int(
            match.group(1)
        )

        return reference_date - timedelta(
            weeks=weeks
        )

    # --------------------------------------------------------
    # MONTHS
    # --------------------------------------------------------

    match = re.match(
        r"^(\d+)\s*months?$",
        raw,
    )

    if match:

        months = int(
            match.group(1)
        )

        return reference_date - timedelta(
            days=months * 30
        )

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    if raw in (
        "today",
        "now",
        "just now",
    ):

        return reference_date

    # --------------------------------------------------------
    # YESTERDAY
    # --------------------------------------------------------

    if raw == "yesterday":

        return reference_date - timedelta(
            days=1
        )

    return None


# ============================================================
# NORMALIZE POST DATE
# ============================================================

def normalize_post_date(
    timestamp,
    scraped_at,
):
    """
    Priority:

    1. Full calendar date with year
    2. Day + month without year
    3. Relative timestamp + Scraped At
    4. Blank if date genuinely cannot be determined

    IMPORTANT:
    We NEVER replace an unknown historical date
    with today's date.
    """

    raw = clean(timestamp)

    if not raw:
        return ""

    scraped_dt = parse_scraped_at(
        scraped_at
    )

    # Use scraped time as the reference.
    # If unavailable, use current IST time only
    # for relative-date interpretation.
    reference_date = (
        scraped_dt
        if scraped_dt
        else datetime.now(IST)
    )

    # ========================================================
    # 1. ISO DATE
    # ========================================================

    if (
        len(raw) >= 10
        and raw[4] == "-"
        and raw[7] == "-"
    ):

        try:

            dt = datetime.strptime(
                raw[:10],
                "%Y-%m-%d",
            )

            return dt.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            pass

    # ========================================================
    # 2. FULL DATE WITH YEAR
    # ========================================================

    # Remove Facebook time part:
    # "19 July at 19:03" -> "19 July"
    date_only = re.split(
        r"\s+at\s+",
        raw,
        flags=re.IGNORECASE,
    )[0].strip()

    full_date_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in full_date_formats:

        try:

            dt = datetime.strptime(
                date_only,
                fmt,
            )

            return dt.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            pass

    # ========================================================
    # 3. DAY + MONTH WITHOUT YEAR
    # ========================================================

    day_month = parse_day_month_without_year(
        raw,
        reference_date,
    )

    if day_month:

        return day_month.strftime(
            "%Y-%m-%d"
        )

    # ========================================================
    # 4. RELATIVE TIMESTAMP
    # ========================================================

    relative_dt = parse_relative_timestamp(
        raw,
        reference_date,
    )

    if relative_dt:

        return relative_dt.strftime(
            "%Y-%m-%d"
        )

    # ========================================================
    # 5. UNKNOWN -> BLANK
    # ========================================================

    return ""


# ============================================================
# GOOGLE SHEETS
# ============================================================

def get_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    credentials = (
        Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=scopes,
        )
    )

    client = gspread.authorize(
        credentials
    )

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    print(
        f"Spreadsheet: {spreadsheet.title}"
    )

    print(
        f"Worksheet: {SHEET_NAME}"
    )

    return spreadsheet.worksheet(
        SHEET_NAME
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("GENERATING PUBLIC DASHBOARD DATA")
    print("=" * 70)

    sheet = get_sheet()

    values = sheet.get_all_values()

    if not values:

        raise RuntimeError(
            f'Google Sheet "{SHEET_NAME}" is empty.'
        )

    headers = values[0]

    print(
        f"Columns found : {len(headers)}"
    )

    print(
        f"Rows found    : {len(values) - 1}"
    )

    rows = []

    blank_authors = 0
    valid_dates = 0
    blank_dates = 0

    relative_dates = 0
    day_month_dates = 0

    # ========================================================
    # PROCESS ROWS
    # ========================================================

    for raw_row in values[1:]:

        row = list(raw_row)

        if len(row) < len(headers):

            row += (
                [""] *
                (
                    len(headers)
                    - len(row)
                )
            )

        record = {
            headers[i]: row[i]
            for i in range(len(headers))
        }

        # ----------------------------------------------------
        # AUTHOR
        # ----------------------------------------------------

        author = clean(
            record.get("Author")
        )

        if not author:

            blank_authors += 1

            continue

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = clean(
            record.get("Timestamp")
        )

        scraped_at = clean(
            record.get("Scraped At")
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        post_date = normalize_post_date(
            timestamp,
            scraped_at,
        )

        record["Post Date"] = post_date

        if post_date:

            valid_dates += 1

        else:

            blank_dates += 1

        # ----------------------------------------------------
        # DEBUG COUNTS
        # ----------------------------------------------------

        lower_timestamp = (
            timestamp.lower()
        )

        if re.match(
            r"^\d+\s*(h|m|d)$",
            lower_timestamp,
        ):

            relative_dates += 1

        elif parse_day_month_without_year(
            timestamp,
            parse_scraped_at(
                scraped_at
            )
            or datetime.now(IST),
        ):

            day_month_dates += 1

        rows.append(
            record
        )

    # ========================================================
    # REMOVE SECRET-LIKE FIELDS
    # ========================================================

    secret_fields = {
        "API Key",
        "GEMINI_API_KEY",
        "Service Account",
        "service_account",
        "Credentials",
        "Password",
        "Token",
    }

    for record in rows:

        for field in secret_fields:

            record.pop(
                field,
                None,
            )

    # ========================================================
    # CREATE JSON
    # ========================================================

    payload = {
        "generated_at":
            datetime.now(
                IST
            ).isoformat(),

        "sheet":
            SHEET_NAME,

        "count":
            len(rows),

        "rows":
            rows,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ),
        encoding="utf-8",
    )

    # ========================================================
    # LOG
    # ========================================================

    print("")
    print("=" * 70)
    print("EXPORT SUMMARY")
    print("=" * 70)

    print(
        f"Valid posts       : {len(rows)}"
    )

    print(
        f"Valid post dates  : {valid_dates}"
    )

    print(
        f"Blank post dates  : {blank_dates}"
    )

    print(
        f"Relative dates    : {relative_dates}"
    )

    print(
        f"Day/month dates   : {day_month_dates}"
    )

    print(
        f"Blank authors     : {blank_authors}"
    )

    print(
        f"Output file       : {OUTPUT_FILE}"
    )

    print("=" * 70)
    print(
        "DASHBOARD DATA GENERATED SUCCESSFULLY"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()