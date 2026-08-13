import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file(
    "credentials/service_account.json",
    scopes=scopes,
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(
    "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
)

for ws in spreadsheet.worksheets():

    print("=" * 50)
    print("Sheet :", ws.title)
    print("Rows  :", ws.row_count)
    print("Cols  :", ws.col_count)