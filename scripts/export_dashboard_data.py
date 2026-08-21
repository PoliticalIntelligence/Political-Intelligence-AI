import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# SCRAPED DATE
# ============================================================

def parse_scraped_at(value):
    """
    Convert Scraped At into a datetime.

    Supports:
        2026-08-21 09:00:00
        2026-08-21T09:00:00
        ISO timestamps with timezone
    """

    raw = clean(value)

    if not raw:
        return None

    # ISO format
    try:
        dt = datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        )

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    except ValueError:
        pass

    # Standard formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:

        try:

            dt = datetime.strptime(raw, fmt)

            return dt.replace(tzinfo=timezone.utc)

        except ValueError:
            pass

    return None


# ============================================================
# FACEBOOK RELATIVE DATE
# ============================================================

def parse_relative_timestamp(value, scraped_at):
    """
    Convert Facebook-style relative timestamps.

    Examples:

        4h
        1h
        2d
        1 week ago
        20 weeks ago
        3 months ago

    Uses Scraped At as the reference point.
    """

    raw = clean(value).lower()

    if not raw or scraped_at is None:
        return None

    # Remove words such as "ago"
    raw = raw.replace("ago", "").strip()

    # ---------------------------
    # HOURS
    # ---------------------------

    match = re.match(
        r"^(\d+)\s*h$",
        raw,
    )

    if match:

        hours = int(match.group(1))

        return scraped_at - timedelta(hours=hours)

    # ---------------------------
    # MINUTES
    # ---------------------------

    match = re.match(
        r"^(\d+)\s*m$",
        raw,
    )

    if match:

        minutes = int(match.group(1))

        return scraped_at - timedelta(minutes=minutes)

    # ---------------------------
    # DAYS
    # ---------------------------

    match = re.match(
        r"^(\d+)\s*d$",
        raw,
    )

    if match:

        days = int(match.group(1))

        return scraped_at - timedelta(days=days)

    # ---------------------------
    # WEEKS
    # ---------------------------

    match = re.match(
        r"^(\d+)\s*weeks?$",
        raw,
    )

    if match:

        weeks = int(match.group(1))

        return scraped_at - timedelta(
            weeks=weeks
        )

    # ---------------------------
    # MONTHS
    # ---------------------------

    match = re.match(
        r"^(\d+)\s*months?$",
        raw,
    )

    if match:

        months = int(match.group(1))

        return scraped_at - timedelta(
            days=months * 30
        )

    return None


# ============================================================
# ACTUAL POST DATE
# ============================================================

def normalize_post_date(timestamp, scraped_at):
    """
    Determine the best available post date.

    Priority:

    1. Actual calendar date
    2. Facebook relative timestamp + Scraped At
    3. Scraped At date
    """

    raw = clean(timestamp)

    if not raw:
        scraped_dt = parse_scraped_at(scraped_at)

        if scraped_dt:
            return scraped_dt.strftime("%Y-%m-%d")

        return ""

    # --------------------------------------------------------
    # Already ISO date
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

            return dt.strftime("%Y-%m-%d")

        except ValueError:

            pass

    # --------------------------------------------------------
    # Normal calendar dates
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

            return dt.strftime("%Y-%m-%d")

        except ValueError:

            pass

    # --------------------------------------------------------
    # Relative timestamp
    # --------------------------------------------------------

    scraped_dt = parse_scraped_at(
        scraped_at
    )

    relative_dt = parse_relative_timestamp(
        raw,
        scraped_dt,
    )

    if relative_dt:

        return relative_dt.strftime(
            "%Y-%m-%d"
        )

    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    if scraped_dt:

        return scraped_dt.strftime(
            "%Y-%m-%d"
        )

    return raw


# ============================================================
# GOOGLE SHEET
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
# EXPORT
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

    converted_relative = 0

    skipped = 0

    # --------------------------------------------------------
    # PROCESS ROWS
    # --------------------------------------------------------

    for raw_row in values[1:]:

        row = list(raw_row)

        if len(row) < len(headers):

            row += [
                ""
            ] * (
                len(headers) - len(row)
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

            skipped += 1

            continue

        # ----------------------------------------------------
        # POST DATE
        # ----------------------------------------------------

        timestamp = clean(
            record.get("Timestamp")
        )

        scraped_at = clean(
            record.get("Scraped At")
        )

        original_date = normalize_post_date(
            timestamp,
            scraped_at,
        )

        if (
            timestamp
            and re.match(
                r"^\d+\s*[hmd]|^\d+\s*weeks?",
                timestamp.lower(),
            )
        ):

            converted_relative += 1

        record["Post Date"] = original_date

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

        rows.append(record)

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    payload = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "sheet": SHEET_NAME,

        "count": len(rows),

        "rows": rows,
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
        f"Skipped blank authors    : {skipped}"
    )

    print(
        f"Relative dates converted : {converted_relative}"
    )

    print(
        f"Output file              : {OUTPUT_FILE}"
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