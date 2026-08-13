from __future__ import annotations

import datetime as dt
import os
import secrets
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

import gspread
from google.oauth2.service_account import Credentials

# Use the same local service-account setup as the working project.
# No dependency on a non-existent core.google_auth module.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def client():
    credentials_path = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        "credentials/service_account.json",
    )
    if not Path(credentials_path).is_absolute():
        credentials_path = str(Path.cwd() / credentials_path)
    if not Path(credentials_path).exists():
        raise FileNotFoundError(
            f"Google service account file not found: {credentials_path}"
        )
    credentials = Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES,
    )
    return gspread.authorize(credentials)

SPREADSHEET_NAME = os.getenv(
    "GOOGLE_SPREADSHEET_NAME",
    "Political Intelligence Database",
)
AI_SHEET = os.getenv("AI_SHEET", "AI Analysis")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
CACHE_TTL = 60

app = FastAPI(title="Political Intelligence Dashboard", version="2.0.0")
security = HTTPBasic(auto_error=False)

_cache = {"timestamp": 0.0, "records": []}
_cache_lock = threading.Lock()


def dashboard_auth(credentials: HTTPBasicCredentials | None = Depends(security)):
    username = os.getenv("DASHBOARD_USERNAME", "").strip()
    password = os.getenv("DASHBOARD_PASSWORD", "")
    if not username and not password:
        return True
    if not credentials or not (
        secrets.compare_digest(credentials.username, username)
        and secrets.compare_digest(credentials.password, password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


def _load_records(force: bool = False) -> list[dict[str, str]]:
    now = time.time()
    with _cache_lock:
        if not force and _cache["records"] and now - _cache["timestamp"] < CACHE_TTL:
            return _cache["records"]

        spreadsheet = client().open(SPREADSHEET_NAME)
        sheet = spreadsheet.worksheet(AI_SHEET)
        values = sheet.get_all_values()
        if not values:
            records = []
        else:
            headers = [str(h).strip() for h in values[0]]
            records = []
            for row in values[1:]:
                padded = list(row) + [""] * max(0, len(headers) - len(row))
                records.append(dict(zip(headers, padded[: len(headers)])))

        _cache["timestamp"] = now
        _cache["records"] = records
        return records


def _clean(value) -> str:
    return str(value or "").strip()


def _valid(records: list[dict[str, str]]) -> list[dict[str, str]]:
    # Author is the master eligibility key: blank Author = not a dashboard post.
    return [r for r in records if _clean(r.get("Author"))]


def _parse_post_date(value: str) -> Optional[dt.date]:
    value = _clean(value)
    if not value:
        return None
    # Handles YYYY-MM-DD, YYYY-MM-DD HH:MM:SS and ISO timestamps.
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(value[:10], fmt).date()
        except ValueError:
            continue
    return None


def _date_text(r: dict[str, str]) -> str:
    parsed = _parse_post_date(_clean(r.get("Timestamp")))
    return parsed.isoformat() if parsed else _clean(r.get("Timestamp"))[:10]


def _contains(r: dict[str, str], keys: tuple[str, ...], needle: str) -> bool:
    needle = needle.lower().strip()
    if not needle:
        return True
    return any(needle in _clean(r.get(k)).lower() for k in keys)


def _filtered(
    records: list[dict[str, str]],
    *,
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
    exact_date: str = "",
    author: str = "",
    district: str = "",
    assembly: str = "",
    category: str = "",
    subcategory: str = "",
    event: str = "",
    party: str = "",
    leader: str = "",
    sector: str = "",
    scheme: str = "",
) -> list[dict[str, str]]:
    result = []
    for r in _valid(records):
        post_date = _parse_post_date(_clean(r.get("Timestamp")))
        if exact_date and _date_text(r) != exact_date:
            continue
        if start and (post_date is None or post_date < start):
            continue
        if end and (post_date is None or post_date > end):
            continue
        if author and _clean(r.get("Author")) != author:
            continue
        if category and _clean(r.get("AI Main Category")) != category:
            continue
        if subcategory and _clean(r.get("AI Sub Category")) != subcategory:
            continue
        if event and _clean(r.get("AI Event Type")) != event:
            continue
        if party and _clean(r.get("AI Party Mentioned")) != party:
            continue
        if leader and leader.lower() not in _clean(r.get("AI Leader Mentioned")).lower():
            continue
        if sector and _clean(r.get("AI Development Sector")) != sector:
            continue
        if scheme and scheme.lower() not in _clean(r.get("AI Government Scheme")).lower():
            continue
        if district and not _contains(r, ("District", "AI District", "Source Page", "AI Place of Visit"), district):
            continue
        if assembly and not _contains(r, ("Assembly", "AC", "Constituency", "AI Assembly", "Source Page", "AI Place of Visit"), assembly):
            continue
        result.append(r)

    result.sort(key=lambda r: (_parse_post_date(_clean(r.get("Timestamp"))) or dt.date.min, _clean(r.get("Timestamp"))), reverse=True)
    return result


def _counter(records: list[dict[str, str]], key: str, limit: int = 12) -> list[dict[str, object]]:
    counter = Counter()
    for r in records:
        value = _clean(r.get(key)) or "Not Classified"
        counter[value] += 1
    return [{"label": k, "value": v} for k, v in counter.most_common(limit)]


def _daily(records: list[dict[str, str]]) -> list[dict[str, object]]:
    counter = Counter(_date_text(r) for r in records if _date_text(r))
    return [{"date": k, "value": counter[k]} for k in sorted(counter)]


def _serialize_post(r: dict[str, str]) -> dict[str, str]:
    return {
        "post_date": _date_text(r),
        "processed_date": _clean(r.get("AI Processed At")),
        "author": _clean(r.get("Author")),
        "category": _clean(r.get("AI Main Category")),
        "subcategory": _clean(r.get("AI Sub Category")),
        "event": _clean(r.get("AI Event Type")),
        "place": _clean(r.get("AI Place of Visit")),
        "sector": _clean(r.get("AI Development Sector")),
        "scheme": _clean(r.get("AI Government Scheme")),
        "department": _clean(r.get("AI Government Department")),
        "party": _clean(r.get("AI Party Mentioned")),
        "leader": _clean(r.get("AI Leader Mentioned")),
        "opposition": _clean(r.get("AI Opposition Mention")),
        "opposition_target": _clean(r.get("AI Opposition Target")),
        "keywords": _clean(r.get("AI Keywords")),
        "summary": _clean(r.get("AI Summary")),
        "url": _clean(r.get("Post URL")),
    }


def _apply_period(
    preset: str,
    date: str,
    from_date: str,
    to_date: str,
) -> tuple[Optional[dt.date], Optional[dt.date], str]:
    today = dt.date.today()
    if date:
        d = _parse_post_date(date)
        return d, d, d.isoformat() if d else ""

    if from_date or to_date:
        start = _parse_post_date(from_date) if from_date else None
        end = _parse_post_date(to_date) if to_date else None
        return start, end, "custom"

    p = (preset or "last7").lower()
    if p == "today":
        return today, today, "today"
    if p == "last30":
        return today - dt.timedelta(days=29), today, "last30"
    if p == "thisweek":
        start = today - dt.timedelta(days=today.weekday())
        return start, today, "thisweek"
    if p == "thismonth":
        return today.replace(day=1), today, "thismonth"
    return today - dt.timedelta(days=6), today, "last7"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filters(_: bool = Depends(dashboard_auth)):
    records = _valid(_load_records())
    unique = lambda key: sorted({_clean(r.get(key)) for r in records if _clean(r.get(key))})
    return {
        "authors": unique("Author"),
        "categories": unique("AI Main Category"),
        "subcategories": unique("AI Sub Category"),
        "events": unique("AI Event Type"),
        "parties": unique("AI Party Mentioned"),
        "leaders": unique("AI Leader Mentioned"),
        "sectors": unique("AI Development Sector"),
        "schemes": unique("AI Government Scheme"),
        "districts": sorted({x for r in records for x in [_clean(r.get("District")), _clean(r.get("AI District"))] if x}),
        "assemblies": sorted({x for r in records for x in [_clean(r.get("Assembly")), _clean(r.get("AC")), _clean(r.get("Constituency")), _clean(r.get("AI Assembly"))] if x}),
        "dates": sorted({_date_text(r) for r in records if _date_text(r)}, reverse=True),
    }


@app.get("/api/summary")
def summary(
    preset: str = Query("last7"),
    date: str = Query(""),
    from_date: str = Query(""),
    to_date: str = Query(""),
    author: str = Query(""),
    district: str = Query(""),
    assembly: str = Query(""),
    category: str = Query(""),
    subcategory: str = Query(""),
    event: str = Query(""),
    party: str = Query(""),
    leader: str = Query(""),
    sector: str = Query(""),
    scheme: str = Query(""),
    _: bool = Depends(dashboard_auth),
):
    start, end, period = _apply_period(preset, date, from_date, to_date)
    records = _filtered(
        _load_records(), start=start, end=end, author=author, district=district,
        assembly=assembly, category=category, subcategory=subcategory, event=event,
        party=party, leader=leader, sector=sector, scheme=scheme,
    )

    political_categories = {"Party Activity", "Political Attack", "Election Campaign", "Booth/Karyakarta", "Political"}
    opposition = sum(1 for r in records if _clean(r.get("AI Opposition Mention")).lower() in {"yes", "true", "1"})

    return {
        "period": {"preset": period, "from": start.isoformat() if start else "", "to": end.isoformat() if end else "", "exact": date},
        "total_posts": len(records),
        "political_posts": sum(1 for r in records if _clean(r.get("AI Main Category")) in political_categories),
        "development_posts": sum(1 for r in records if _clean(r.get("AI Main Category")) == "Development"),
        "law_order_posts": sum(1 for r in records if _clean(r.get("AI Main Category")) in {"Law & Order", "Law and Order"}),
        "welfare_posts": sum(1 for r in records if any(x in _clean(r.get("AI Main Category")).lower() for x in ("welfare", "women"))),
        "opposition_mentions": opposition,
        "daily": _daily(records),
        "categories": _counter(records, "AI Main Category"),
        "subcategories": _counter(records, "AI Sub Category"),
        "sectors": _counter(records, "AI Development Sector"),
        "parties": _counter(records, "AI Party Mentioned"),
        "leaders": _counter(records, "AI Leader Mentioned"),
        "events": _counter(records, "AI Event Type"),
        "posts": [_serialize_post(r) for r in records[:250]],
    }


@app.post("/api/refresh")
def refresh(_: bool = Depends(dashboard_auth)):
    _load_records(force=True)
    return {"status": "refreshed"}


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
