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
# BASIC HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# SCRAPED DATE PARSER
# ============================================================

def parse_scraped_at(value):
    raw = clean(value)

    if not raw:
        return None

    # ISO timestamps
    try:
        dt = datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        )

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)

        return dt.astimezone(IST)

    except ValueError:
        pass

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
# RELATIVE FACEBOOK TIMESTAMP
# ============================================================

def parse_relative_timestamp(
    value,
    reference_time,
):
    """
    Converts Facebook-style relative values.

    Examples:
        4h
        2h
        1d
        3d
        2 weeks
        20 weeks ago
        1 month ago
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

        return reference_time - timedelta(
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

        return reference_time - timedelta(
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

        return reference_time - timedelta(
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

        return reference_time - timedelta(
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

        return reference_time - timedelta(
            days=months * 30
        )

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    if raw in (
        "today",
        "just now",
        "now",
    ):
        return reference_time

    # --------------------------------------------------------
    # YESTERDAY
    # --------------------------------------------------------

    if raw == "yesterday":
        return reference_time - timedelta(
            days=1
        )

    return None


# ============================================================
# NORMALIZE POST DATE
# ============================================================

def normalize_post_date(
    timestamp,
    scraped_at,
    fallback_reference,
):
    """
    Determine the best available calendar date.

    Priority:
        1. Actual calendar date
        2. Relative timestamp + Scraped At
        3. Relative timestamp + export/run time
        4. Scraped At date
        5. Export/run date
    """

    raw = clean(timestamp)

    # --------------------------------------------------------
    # Empty timestamp
    # --------------------------------------------------------

    if not raw:

        scraped_dt = parse_scraped_at(
            scraped_at
        )

        if scraped_dt:
            return scraped_dt.strftime(
                "%Y-%m-%d"
            )

        return fallback_reference.strftime(
            "%Y-%m-%d"
        )

    # --------------------------------------------------------
    # ISO DATE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # NORMAL CALENDAR DATES
    # --------------------------------------------------------

    date_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in date_formats:

        try:
            dt = datetime.strptime(
                raw,
                fmt,
            )

            return dt.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # RELATIVE TIMESTAMP
    # --------------------------------------------------------

    scraped_dt = parse_scraped_at(
        scraped_at
    )

    reference = (
        scraped_dt
        if scraped_dt
        else fallback_reference
    )

    relative_dt = parse_relative_timestamp(
        raw,
        reference,
    )

    if relative_dt:

        return relative_dt.strftime(
            "%Y-%m-%d"
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if scraped_dt:

        return scraped_dt.strftime(
            "%Y-%m-%d"
        )

    return fallback_reference.strftime(
        "%Y-%m-%d"
    )


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

    return spreadsheet.worksheet(
        SHEET_NAME
    )


# ============================================================
# MAIN EXPORT
# ============================================================

def main():

    print("=" * 70)
    print("GENERATING PUBLIC DASHBOARD DATA")
    print("=" * 70)

    # Current run time in IST.
    fallback_reference = datetime.now(
        IST
    )

    print(
        f"Export reference time: "
        f"{fallback_reference.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

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
    relative_dates = 0

    examples = []

    # --------------------------------------------------------
    # PROCESS ROWS
    # --------------------------------------------------------

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
        # VALID POST RULE
        # ----------------------------------------------------

        author = clean(
            record.get("Author")
        )

        if not author:

            blank_authors += 1

            continue

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        timestamp = clean(
            record.get("Timestamp")
        )

        scraped_at = clean(
            record.get("Scraped At")
        )

        post_date = normalize_post_date(
            timestamp,
            scraped_at,
            fallback_reference,
        )

        record["Post Date"] = post_date

        # ----------------------------------------------------
        # LOG RELATIVE VALUES
        # ----------------------------------------------------

        if re.match(
            r"^\d+\s*(h|m|d)$",
            timestamp.lower(),
        ):

            relative_dates += 1

            if len(examples) < 15:

                examples.append(
                    (
                        author,
                        timestamp,
                        scraped_at,
                        post_date,
                    )
                )

        # ----------------------------------------------------
        # REMOVE SECRET-LIKE FIELDS
        # ----------------------------------------------------

        secret_fields = {
            "API Key",
            "GEMINI_API_KEY",
            "Service Account",
            "service_account",
            "Credentials",
            "Password",
            "Token",
        }

        for field in secret_fields:

            record.pop(
                field,
                None,
            )

        rows.append(
            record
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    payload = {
        "generated_at":
            fallback_reference.isoformat(),

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

    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    print("")
    print(
        f"Valid posts              : {len(rows)}"
    )

    print(
        f"Skipped blank authors    : {blank_authors}"
    )

    print(
        f"Relative dates converted : {relative_dates}"
    )

    if examples:

        print("")
        print(
            "RELATIVE DATE EXAMPLES:"
        )

        for (
            author,
            timestamp,
            scraped_at,
            post_date,
        ) in examples:

            print(
                f"{author} | "
                f"{timestamp} | "
                f"{scraped_at} -> "
                f"{post_date}"
            )

    print("")
    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print("=" * 70)
    print(
        "DASHBOARD DATA GENERATED SUCCESSFULLY"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()