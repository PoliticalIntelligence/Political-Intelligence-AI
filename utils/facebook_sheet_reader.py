import gspread
from google.oauth2.service_account import Credentials


class FacebookSheetReader:
    """
    Reads Facebook pages from Google Sheets.

    Expected columns:

    ID
    Name
    Facebook URL
    Status
    """

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    CREDENTIALS_PATH = "credentials/service_account.json"

    SPREADSHEET_NAME = "Facebook links"

    WORKSHEET_NAME = "Sheet1"

    def __init__(self):

        credentials = Credentials.from_service_account_file(
            self.CREDENTIALS_PATH,
            scopes=self.SCOPES,
        )

        client = gspread.authorize(credentials)

        self.sheet = (
            client
            .open(self.SPREADSHEET_NAME)
            .worksheet(self.WORKSHEET_NAME)
        )

    # ---------------------------------------------------------
    # Get Active Facebook Pages
    # ---------------------------------------------------------

    def get_pages(self):

        rows = self.sheet.get_all_records()

        pages = []

        for row in rows:

            status = str(
                row.get("Status", "")
            ).strip().lower()

            if status != "active":
                continue

            name = str(
                row.get("Name", "")
            ).strip()

            url = str(
                row.get("Facebook URL", "")
            ).strip()

            if not name or not url:
                continue

            pages.append(
                {
                    "id": int(row["ID"]),
                    "name": name,
                    "url": url,
                }
            )

        pages.sort(key=lambda page: page["id"])

        return pages


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    reader = FacebookSheetReader()

    pages = reader.get_pages()

    print()
    print("=" * 70)
    print(f"Loaded {len(pages)} Facebook Pages")
    print("=" * 70)

    for page in pages:

        print()

        print(f"ID   : {page['id']}")
        print(f"Name : {page['name']}")
        print(f"URL  : {page['url']}")

    print()
    print("=" * 70)
    print("FACEBOOK SHEET READER TEST PASSED")
    print("=" * 70)