from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


class SheetWriter:

    def __init__(
        self,
        logger,
        credentials_path="credentials/service_account.json",
    ):

        self.logger = logger
        self.credentials_path = credentials_path

        self.spreadsheet_id = "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
        self.sheet_name = "AI Analysis"

        self.sheet = None

        self.connect()

    # ----------------------------------------------------------
    # CONNECT
    # ----------------------------------------------------------

    def connect(self):

        self.logger.log("Connecting to AI Analysis...")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes,
        )

        client = gspread.authorize(credentials)

        spreadsheet = client.open_by_key(
            self.spreadsheet_id
        )

        try:

            self.sheet = spreadsheet.worksheet(
                self.sheet_name
            )

        except gspread.WorksheetNotFound:

            self.logger.log(
                "Creating AI Analysis worksheet..."
            )

            self.sheet = spreadsheet.add_worksheet(
                title=self.sheet_name,
                rows=1000,
                cols=26,
            )

        self.create_headers_if_missing()

    # ----------------------------------------------------------
    # CREATE HEADERS
    # ----------------------------------------------------------

    def create_headers_if_missing(self):

        headers = [

            "Post URL",
            "Post Text",
            "Author",
            "Timestamp",
            "Source Page",

            "AI Main Category",
            "AI Sub Category",
            "AI Event Type",

            "AI Place of Visit",

            "Latitude",
            "Longitude",
            "Geo Status",
            "Geo Source",

            "AI Location Type",
            "AI Beneficiary Group",
            "AI Development Sector",
            "AI Government Scheme",
            "AI Government Department",
            "AI Party Mentioned",
            "AI Leader Mentioned",
            "AI Mentioned Persons",
            "AI Opposition Mention",
            "AI Opposition Target",
            "AI Keywords",
            "AI Summary",
            "AI Processed At"

        ]

        first_row = self.sheet.row_values(1)

        if first_row != headers:

            self.logger.log(
                "Creating AI Analysis headers..."
            )

            self.sheet.clear()

            self.sheet.update(
                "A1:Z1",
                [headers]
            )

    # ----------------------------------------------------------
    # WRITE ONE ROW
    # ----------------------------------------------------------

    def append_analysis(self, post, ai, geo):

        row = [

            # ---------------------------------
            # Facebook Post
            # ---------------------------------

            post.url or "",
            post.text or "",
            post.author or "",
            post.timestamp or "",
            post.source_page or "",

            # ---------------------------------
            # AI
            # ---------------------------------

            ai.get("main_category", ""),
            ai.get("sub_category", ""),
            ai.get("event_type", ""),

            ", ".join(ai.get("place_of_visit", [])),

            # ---------------------------------
            # GIS
            # ---------------------------------

            geo.get("latitude", ""),
            geo.get("longitude", ""),
            geo.get("status", ""),
            geo.get("source", ""),

            # ---------------------------------
            # Remaining AI Fields
            # ---------------------------------

            ai.get("location_type", ""),
            ai.get("beneficiary_group", ""),
            ai.get("development_sector", ""),
            ai.get("government_scheme", ""),
            ai.get("government_department", ""),
            ai.get("party_mentioned", ""),
            ai.get("leader_mentioned", ""),

            ", ".join(ai.get("mentioned_persons", [])),

            "Yes" if ai.get("opposition_mention", False) else "No",

            ai.get("opposition_target", ""),

            ", ".join(ai.get("keywords", [])),

            ai.get("summary", ""),

            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ]

        next_row = len(self.sheet.col_values(1)) + 1

        self.logger.log(
            f"Writing AI output to row {next_row}"
        )

        self.sheet.update(
            f"A{next_row}:Z{next_row}",
            [row],
            value_input_option="USER_ENTERED"
        )

        self.logger.log("AI row written successfully.")