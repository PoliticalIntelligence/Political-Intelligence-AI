import gspread
from google.oauth2.service_account import Credentials


class SheetReader:
    """
    Reads data from Google Sheets.
    """

    def __init__(
        self,
        logger,
        credentials_path="credentials/service_account.json",
    ):

        self.logger = logger
        self.credentials_path = credentials_path

        self.spreadsheet_id = "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"

        self.raw_sheet_name = "Raw_Posts"
        self.ai_sheet_name = "AI Analysis"

        self.client = None
        self.raw_sheet = None
        self.ai_sheet = None

        self.connect()

    # -----------------------------------------------------
    # CONNECT
    # -----------------------------------------------------

    def connect(self):

        self.logger.log("Connecting to Google Sheets...")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes,
        )

        self.client = gspread.authorize(credentials)

        spreadsheet = self.client.open_by_key(
            self.spreadsheet_id
        )

        self.raw_sheet = spreadsheet.worksheet(
            self.raw_sheet_name
        )

        self.ai_sheet = spreadsheet.worksheet(
            self.ai_sheet_name
        )

        self.logger.log("Google Sheets connected.")

    # -----------------------------------------------------
    # RAW POSTS
    # -----------------------------------------------------

    def get_raw_posts(self):

        records = self.raw_sheet.get_all_records()

        self.logger.log(
            f"Loaded {len(records)} posts from Raw_Posts."
        )

        return records

    # -----------------------------------------------------
    # AI URLS
    # -----------------------------------------------------

    def get_processed_urls(self):

        values = self.ai_sheet.col_values(1)

        if len(values) <= 1:
            return set()

        urls = set(values[1:])

        self.logger.log(
            f"Found {len(urls)} processed posts."
        )

        return urls

    # -----------------------------------------------------
    # NEW POSTS
    # -----------------------------------------------------

    def get_new_posts(self):

        raw_posts = self.get_raw_posts()

        processed_urls = self.get_processed_urls()

        new_posts = []

        for post in raw_posts:

            url = post.get("Post URL", "").strip()

            if not url:
                continue

            if url in processed_urls:
                continue

            new_posts.append(post)

        self.logger.log(
            f"{len(new_posts)} new posts require AI analysis."
        )

        return new_posts