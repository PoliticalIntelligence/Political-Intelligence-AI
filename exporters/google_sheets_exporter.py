from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsExporter:
    """
    Export Facebook posts to Google Sheets.

    Permanent master sheet:
        Raw_Posts

    Daily log:
        One worksheet per run date, e.g. 2026-08-10
    """

    HEADERS = [
        "Scraped At",
        "Author",
        "Timestamp",
        "Post URL",
        "Post Text",
        "Reactions",
        "Comments",
        "Shares",
        "Like",
        "Love",
        "Care",
        "Haha",
        "Wow",
        "Sad",
        "Angry",
        "Images",
        "Videos",
        "Source Page",
    ]

    def __init__(
        self,
        logger,
        credentials_path="credentials/service_account.json",
    ):

        self.logger = logger
        self.credentials_path = credentials_path

        # YOUR SPREADSHEET ID
        self.spreadsheet_id = (
            "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
        )

        self.worksheet_name = "Raw_Posts"

        self.client = None
        self.spreadsheet = None
        self.sheet = None

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

        self.logger.log("Google authentication successful.")

        self.spreadsheet = self.client.open_by_key(
            self.spreadsheet_id
        )

        self.logger.log("Spreadsheet opened successfully.")

        print(
            f"Spreadsheet URL : "
            f"https://docs.google.com/spreadsheets/d/"
            f"{self.spreadsheet.id}"
        )

        try:

            self.sheet = self.spreadsheet.worksheet(
                self.worksheet_name
            )

            self.logger.log(
                f"Using worksheet: {self.worksheet_name}"
            )

        except gspread.WorksheetNotFound:

            self.logger.log(
                "Worksheet not found. Creating..."
            )

            self.sheet = self.spreadsheet.add_worksheet(
                title=self.worksheet_name,
                rows=5000,
                cols=30,
            )

            self.logger.log("Worksheet created.")

        self.create_headers(self.sheet)

    # -----------------------------------------------------
    # HEADERS
    # -----------------------------------------------------

    def create_headers(self, worksheet):

        first_row = worksheet.row_values(1)

        if first_row != self.HEADERS:

            # Only initialize a completely empty worksheet.
            # Do NOT clear an existing populated sheet.
            if not first_row:

                worksheet.append_row(
                    self.HEADERS,
                    value_input_option="USER_ENTERED",
                )

                self.logger.log(
                    f"Headers created in: {worksheet.title}"
                )

            else:

                self.logger.log(
                    f"Headers already exist / differ in: "
                    f"{worksheet.title}"
                )

        else:

            self.logger.log(
                f"Headers already exist in: {worksheet.title}"
            )

    # -----------------------------------------------------
    # DAILY WORKSHEET
    # -----------------------------------------------------

    def get_daily_worksheet(self, run_date):

        # Expected format: YYYY-MM-DD
        try:

            datetime.strptime(
                run_date,
                "%Y-%m-%d"
            )

        except ValueError:

            raise ValueError(
                f"Invalid run date '{run_date}'. "
                f"Use YYYY-MM-DD."
            )

        try:

            daily_sheet = self.spreadsheet.worksheet(
                run_date
            )

            self.logger.log(
                f"Using daily worksheet: {run_date}"
            )

        except gspread.WorksheetNotFound:

            self.logger.log(
                f"Daily worksheet '{run_date}' not found. "
                f"Creating..."
            )

            daily_sheet = self.spreadsheet.add_worksheet(
                title=run_date,
                rows=5000,
                cols=len(self.HEADERS),
            )

            self.create_headers(daily_sheet)

            self.logger.log(
                f"Daily worksheet created: {run_date}"
            )

        return daily_sheet

    # -----------------------------------------------------
    # EXISTING URLS
    # -----------------------------------------------------

    def get_existing_urls(self):

        urls = self.sheet.col_values(4)

        if len(urls) <= 1:

            return set()

        return set(
            url.strip()
            for url in urls[1:]
            if url.strip()
        )

    # -----------------------------------------------------
    # BUILD ROW
    # -----------------------------------------------------

    def build_row(self, post):

        return [
            post.scraped_at
            or datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            getattr(post, "author", ""),

            post.timestamp,

            post.url,

            post.text,

            post.reactions,

            post.comments,

            post.shares,

            post.like,

            post.love,

            post.care,

            post.haha,

            post.wow,

            post.sad,

            post.angry,

            "\n".join(post.images),

            "\n".join(post.videos),

            post.source_page,
        ]

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    def export(self, posts, run_date=None):

        if run_date is None:

            run_date = datetime.now().strftime(
                "%Y-%m-%d"
            )

        self.logger.log(
            f"Preparing Google Sheets export "
            f"for run date: {run_date}"
        )

        # Create/find today's log tab before processing.
        daily_sheet = self.get_daily_worksheet(
            run_date
        )

        existing_urls = self.get_existing_urls()

        new_rows = []
        duplicate_count = 0

        for post in posts:

            if not post.url:

                continue

            if post.url in existing_urls:

                duplicate_count += 1
                continue

            existing_urls.add(post.url)

            new_rows.append(
                self.build_row(post)
            )

        if not new_rows:

            self.logger.log(
                "No new posts to upload."
            )

            print("=" * 70)
            print("GOOGLE SHEETS EXPORT")
            print("=" * 70)
            print(
                f"Run Date       : {run_date}"
            )
            print(
                f"New Posts      : 0"
            )
            print(
                f"Duplicates     : {duplicate_count}"
            )
            print(
                f"Daily Worksheet: {daily_sheet.title}"
            )
            print("=" * 70)

            return

        self.logger.log(
            f"Uploading {len(new_rows)} new posts..."
        )

        try:

            # 1. Permanent master data
            self.sheet.append_rows(
                new_rows,
                value_input_option="USER_ENTERED",
            )

            self.logger.log(
                f"Added {len(new_rows)} rows to "
                f"{self.worksheet_name}"
            )

            # 2. Daily run log
            daily_sheet.append_rows(
                new_rows,
                value_input_option="USER_ENTERED",
            )

            self.logger.log(
                f"Added {len(new_rows)} rows to "
                f"daily worksheet {run_date}"
            )

            print("=" * 70)
            print("GOOGLE SHEETS EXPORT")
            print("=" * 70)
            print(
                f"Run Date       : {run_date}"
            )
            print(
                f"Master Sheet   : {self.worksheet_name}"
            )
            print(
                f"Daily Worksheet: {run_date}"
            )
            print(
                f"Rows Added     : {len(new_rows)}"
            )
            print(
                f"Duplicates     : {duplicate_count}"
            )
            print(
                f"Spreadsheet    : "
                f"https://docs.google.com/spreadsheets/d/"
                f"{self.spreadsheet_id}"
            )
            print("=" * 70)

        except Exception as e:

            self.logger.log(
                f"Google Sheets upload failed: {e}"
            )

            raise

        self.logger.log(
            "Google Sheets export finished."
        )

        self.logger.log(
            f"New Posts      : {len(new_rows)}"
        )

        self.logger.log(
            f"Duplicates     : {duplicate_count}"
        )

        self.logger.log(
            f"Total Scraped  : {len(posts)}"
        )
