from browser.browser_manager import BrowserManager
from core.config import Config
from collectors.facebook_parser import FacebookParser


class FacebookCollector:

    def __init__(self, browser_manager: BrowserManager):

        self.browser_manager = browser_manager

        self.context = None
        self.page = None

        self.parser = None

        print("Facebook Collector Initialized")

    def open_page(self, url):

        print(f"\nOpening Facebook page:\n{url}")

        self.context = self.browser_manager.create_context()

        self.page = self.context.new_page()

        self.page.goto(
            url,
            wait_until="networkidle",
            timeout=Config.DEFAULT_TIMEOUT
        )

        self.parser = FacebookParser(self.page)

        print(f"Page Title: {self.page.title()}")

    def get_dummy_post(self):

        return self.parser.create_dummy_post()

    def close_page(self):

        if self.context:
            self.context.close()

        print("Facebook page closed.")