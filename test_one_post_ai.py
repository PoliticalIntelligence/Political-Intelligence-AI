"""
ONE-POST AI PIPELINE TEST - FINAL

Forces exactly one post through the AI pipeline using a synthetic
test URL so duplicate protection does not skip it.

No Facebook scraping.
No Raw_Posts changes.
One AI Analysis test row may be created.

Run:
    python test_one_post_ai.py
"""

import os

import gspread
from google.oauth2.service_account import Credentials

from processors.ai_processor import AIProcessor
from utils.logger import Logger


SPREADSHEET_ID = "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "credentials/service_account.json",
)
AI_SHEET_NAME = "AI Analysis"


class PostDict(dict):
    """Dictionary that also behaves like the real Post model."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


# ---------------------------------------------------------
# EXACT RAMAKANT YADAV CONTENT
# ---------------------------------------------------------

POST = PostDict({
    # Synthetic URL intentionally used only for this test.
    "Post URL": "TEST://RamakantYadav/2026-08-13/AI-CLOUD-TEST",

    "Post Text": (
        "अत्याचार व शोषण के खिलाफ़ अपनी आवाज़ बुलंद करने वाली सामाजिक न्याय की "
        "योद्धा, समाजवादी पार्टी की पूर्व सांसद स्व. फूलन देवी जी की पुण्यतिथि "
        "पर भावभीनी श्रद्धांजलि।"
    ),

    "Author": "Ramakant Yadav",
    "Timestamp": "25 July 2022",
    "Source Page": "https://www.facebook.com/RamakantYadavmp/",
    "Scraped At": "2026-08-12 18:53:02",

    "Reactions": 2,
    "Comments": 25,
    "Shares": 0,
})

# ---------------------------------------------------------
# REAL POST OBJECT COMPATIBILITY
# ---------------------------------------------------------

POST["url"] = POST["Post URL"]
POST["text"] = POST["Post Text"]
POST["author"] = POST["Author"]
POST["timestamp"] = POST["Timestamp"]
POST["source_page"] = POST["Source Page"]
POST["scraped_at"] = POST["Scraped At"]

POST["page_name"] = POST["Author"]
POST["page_url"] = POST["Source Page"]
POST["page_id"] = ""

# The real Post object also has these attributes.
POST["reactions"] = POST["Reactions"]
POST["comments"] = POST["Comments"]
POST["shares"] = POST["Shares"]
POST["like"] = 0
POST["love"] = 0
POST["care"] = 0
POST["haha"] = 0
POST["wow"] = 0
POST["sad"] = 0
POST["angry"] = 0
POST["images"] = []
POST["videos"] = []


def get_ai_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=scopes,
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    return spreadsheet.worksheet(AI_SHEET_NAME)


def main():
    print("=" * 70)
    print("FINAL ONE-POST AI PIPELINE TEST")
    print("=" * 70)
    print("Author :", POST["Author"])
    print("Date   :", POST["Timestamp"])
    print("URL    :", POST["Post URL"])
    print("AI     : ON")
    print("Scraper: OFF")
    print("Raw    : NOT MODIFIED")
    print("=" * 70)

    # ---------------------------------------------------------
    # Avoid repeating this synthetic test if it already exists.
    # ---------------------------------------------------------

    sheet = get_ai_sheet()
    headers = sheet.row_values(1)

    if "Post URL" not in headers:
        raise RuntimeError(
            '"Post URL" column not found in AI Analysis.'
        )

    url_col = headers.index("Post URL") + 1

    existing_urls = {
        value.strip()
        for value in sheet.col_values(url_col)[1:]
        if value.strip()
    }

    if POST["Post URL"] in existing_urls:
        print("Synthetic test row already exists.")
        print("No duplicate row will be created.")
        return

    # ---------------------------------------------------------
    # RUN EXACTLY ONE POST
    # ---------------------------------------------------------

    logger = Logger()
    processor = AIProcessor(logger)
    processor.run([POST])

    print("")
    print("=" * 70)
    print("FINAL ONE-POST AI TEST FINISHED")
    print("=" * 70)
    print("Check AI Analysis for:")
    print(POST["Post URL"])
    print("=" * 70)


if __name__ == "__main__":
    main()
