import time

from browser.browser_manager import BrowserManager
from core.config import Config

from collectors.facebook.historical_crawler import HistoricalFacebookCrawler


class HistoricalFacebookCollector:
    """
    High-level orchestrator for historical Facebook scraping.
    """

    def __init__(
        self,
        browser_manager: BrowserManager,
        history_days: int = 45,
    ):

        self.browser_manager = browser_manager

        self.history_days = history_days

        self.context = None
        self.page = None

        self.crawler = None

    # ----------------------------------------------------
    # Open Facebook Page
    # ----------------------------------------------------

    def open_page(self, url: str):

        print("\n" + "=" * 70)
        print("OPENING FACEBOOK PAGE")
        print("=" * 70)

        print(url)

        self.context = self.browser_manager.create_context()

        self.page = self.context.new_page()

        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=Config.DEFAULT_TIMEOUT,
        )

        self.page.wait_for_selector(
            "div[role='main']",
            timeout=15000,
        )

        time.sleep(2)

        self.close_login_popup()

        time.sleep(1)

        print()
        print("Title :", self.page.title())
        print("URL   :", self.page.url)
        print()

        self.crawler = HistoricalFacebookCrawler(
            page=self.page,
            history_days=self.history_days,
        )

    # ----------------------------------------------------
    # Close Login Popup
    # ----------------------------------------------------

    def close_login_popup(self):

        try:

            dialog = self.page.locator("[role='dialog']")

            if dialog.count() == 0:
                return

            buttons = dialog.locator(
                "[aria-label='Close'], [aria-label='close']"
            )

            if buttons.count():

                print("Closing login popup...")

                buttons.first.click(timeout=2000)

                time.sleep(1)

                print("Popup closed.")

        except Exception:

            pass

    # ----------------------------------------------------
    # Crawl
    # ----------------------------------------------------

    def get_posts(self):

        if self.crawler is None:
            raise Exception("Page has not been opened.")

        print()
        print("=" * 70)
        print("STARTING HISTORICAL FACEBOOK CRAWLER")
        print("=" * 70)

        return self.crawler.run()

    # ----------------------------------------------------
    # Close
    # ----------------------------------------------------

    def close(self):

        try:

            if self.context:

                self.context.close()

                print("\nFacebook page closed.")

        except Exception:

            pass