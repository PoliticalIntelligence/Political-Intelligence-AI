"""
Cloud-safe scraper state.

Uses Google Sheets Raw_Posts as persistent source of truth for
previously scraped Post URLs. Keeps a current-process in-memory cache.
"""

import os
from typing import Iterable, Set, Optional

import gspread
from google.oauth2.service_account import Credentials


class ScraperState:
    DEFAULT_SPREADSHEET_ID = (
        "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
    )
    DEFAULT_WORKSHEET = "Raw_Posts"
    DEFAULT_CREDENTIALS = "credentials/service_account.json"

    def __init__(
        self,
        spreadsheet_id: Optional[str] = None,
        worksheet_name: Optional[str] = None,
        credentials_path: Optional[str] = None,
        refresh_from_sheet: bool = True,
    ):
        self.spreadsheet_id = (
            spreadsheet_id
            or os.getenv("GOOGLE_SHEETS_ID")
            or self.DEFAULT_SPREADSHEET_ID
        )
        self.worksheet_name = (
            worksheet_name
            or os.getenv("RAW_POSTS_SHEET")
            or self.DEFAULT_WORKSHEET
        )
        self.credentials_path = (
            credentials_path
            or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
            or self.DEFAULT_CREDENTIALS
        )

        self.known_posts: Set[str] = set()
        self.sheet = None

        if refresh_from_sheet:
            self._load_from_google_sheets()

    def _load_from_google_sheets(self) -> None:
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google service-account file not found: "
                f"{self.credentials_path}"
            )

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes,
        )

        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(self.spreadsheet_id)

        try:
            self.sheet = spreadsheet.worksheet(self.worksheet_name)
        except gspread.WorksheetNotFound as exc:
            raise RuntimeError(
                f"Worksheet '{self.worksheet_name}' was not found "
                f"in spreadsheet '{spreadsheet.title}'."
            ) from exc

        headers = self.sheet.row_values(1)

        try:
            url_column = headers.index("Post URL") + 1
        except ValueError as exc:
            raise RuntimeError(
                f'Worksheet "{self.worksheet_name}" does not contain '
                '"Post URL" header.'
            ) from exc

        urls = self.sheet.col_values(url_column)

        for url in urls[1:]:
            cleaned = str(url).strip()
            if cleaned:
                self.known_posts.add(cleaned)

        print(
            f"[ScraperState] Loaded {len(self.known_posts)} existing "
            f"post URLs from Google Sheets."
        )

    def is_known(self, url: str) -> bool:
        cleaned = str(url or "").strip()
        if not cleaned:
            return False
        return cleaned in self.known_posts

    def update(self, urls: Iterable[str]) -> None:
        """
        Update only the in-memory current-run cache.

        Persistent writes remain the responsibility of the Raw_Posts
        exporter, so URLs are not written twice.
        """
        added = 0

        for url in urls:
            cleaned = str(url or "").strip()
            if not cleaned:
                continue

            if cleaned not in self.known_posts:
                self.known_posts.add(cleaned)
                added += 1

        print(
            f"[ScraperState] Added {added} URLs to current-run state. "
            f"Total cached URLs: {len(self.known_posts)}."
        )

    def refresh(self) -> None:
        """Reload the persistent URL cache from Google Sheets."""
        self.known_posts.clear()
        self._load_from_google_sheets()
