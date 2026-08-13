import os

import gspread
from google.oauth2.service_account import Credentials

from ai_classifier.classifier import AIClassifier
from ai_classifier.knowledge_engine import KnowledgeEngine
from knowledge_base.political_lookup import PoliticalLookup
from gis.geocoder import GeoCoder

# ==========================================================
# GOOGLE SHEETS
# ==========================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SERVICE_ACCOUNT_FILE = "credentials/service_account.json"

SPREADSHEET_NAME = "Political Intelligence Database"

RAW_SHEET = "Raw_Posts"
AI_SHEET = "AI Analysis"


# ==========================================================
# CONNECT
# ==========================================================

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

spreadsheet = gc.open(SPREADSHEET_NAME)

raw_sheet = spreadsheet.worksheet(RAW_SHEET)
ai_sheet = spreadsheet.worksheet(AI_SHEET)


# ==========================================================
# AI
# ==========================================================

API_KEY = os.getenv("GEMINI_API_KEY")

classifier = AIClassifier(API_KEY)
knowledge_engine = KnowledgeEngine()


# ==========================================================
# LOAD DATA
# ==========================================================

raw_records = raw_sheet.get_all_records()

processed_rows = set()

try:

    existing = ai_sheet.get_all_records()

    for row in existing:

        processed_rows.add(str(row["Raw Row"]))

except Exception:
    pass


rows_to_append = []


# ==========================================================
# PROCESS
# ==========================================================

for index, row in enumerate(raw_records, start=2):

    row_id = str(index)

    if row_id in processed_rows:
        continue

    caption = row.get("Caption", "")

    if not caption.strip():
        continue

    print(f"Processing Row {row_id}")

    result = classifier.classify(caption)

    result = knowledge_engine.enrich(result)

    rows_to_append.append([

        row_id,

        row.get("Facebook Page", ""),
        row.get("Post Date", ""),
        caption,

        result["main_category"],
        result["sub_category"],
        result["event_type"],

        ", ".join(result["place_of_visit"]),

        result["location_type"],
        result["beneficiary_group"],
        result["development_sector"],
        result["government_scheme"],
        result["government_department"],
        result["party_mentioned"],
        result["leader_mentioned"],

        ", ".join(result["mentioned_persons"]),

        result["opposition_mention"],
        result["opposition_target"],

        ", ".join(result["keywords"]),

        result["summary"]

    ])


# ==========================================================
# WRITE
# ==========================================================

if rows_to_append:

    ai_sheet.append_rows(rows_to_append)

    print(f"{len(rows_to_append)} rows written.")

else:

    print("No new rows found.")