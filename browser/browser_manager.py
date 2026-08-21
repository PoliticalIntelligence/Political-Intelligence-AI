import os
import sys

from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self, logger):

        self.logger = logger

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # ------------------------------------------------------
    # HEADLESS DETECTION
    # ------------------------------------------------------

    def is_headless_environment(self):

        # Explicit override
        env_value = os.getenv(
            "PLAYWRIGHT_HEADLESS"
        )

        if env_value is not None:

            return env_value.lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

        # GitHub Actions
        if os.getenv(
            "GITHUB_ACTIONS"
        ) == "true":

            return True

        # Linux without DISPLAY
        if sys.platform.startswith(
            "linux"
        ) and not os.getenv(
            "DISPLAY"
        ):

            return True

        # Local Windows / normal desktop
        return False

    # ------------------------------------------------------
    # START PLAYWRIGHT
    # ------------------------------------------------------

    def start(self):

        self.logger.log(
            "=" * 70
        )

        self.logger.log(
            "STARTING PLAYWRIGHT"
        )

        self.logger.log(
            "=" * 70
        )

        self.logger.log(
            "Starting Playwright..."
        )

        self.playwright = (
            sync_playwright().start()
        )

        headless = (
            self.is_headless_environment()
        )

        self.logger.log(
            f"Browser mode : "
            f"{'HEADLESS' if headless else 'HEADED'}"
        )

        self.logger.log(
            "Launching Chromium..."
        )

        self.browser = (
            self.playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-notifications",
                    "--disable-popup-blocking",
                    "--disable-infobars",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
        )

        self.logger.log(
            "Chromium launched successfully."
        )

        return self.browser

    # ------------------------------------------------------
    # CONTEXT
    # ------------------------------------------------------

    def new_context(self):

        if not self.browser:

            raise RuntimeError(
                "Browser has not been started."
            )

        self.logger.log(
            "Creating browser context..."
        )

        self.context = (
            self.browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 900,
                },

                locale="en-IN",

                timezone_id="Asia/Kolkata",

                user_agent=(
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/138.0.0.0 "
                    "Safari/537.36"
                ),
            )
        )

        self.logger.log(
            "Browser context created."
        )

        return self.context

    # ------------------------------------------------------
    # PAGE
    # ------------------------------------------------------

    def new_page(self):

        if not self.context:

            self.new_context()

        self.page = (
            self.context.new_page()
        )

        return self.page

    # ------------------------------------------------------
    # CLOSE
    # ------------------------------------------------------

    def close(self):

        try:

            if self.page:

                try:
                    self.page.close()
                except Exception:
                    pass

                self.page = None

            if self.context:

                try:
                    self.context.close()
                except Exception:
                    pass

                self.context = None

            if self.browser:

                try:
                    self.browser.close()
                except Exception:
                    pass

                self.browser = None

        finally:

            if self.playwright:

                try:
                    self.playwright.stop()
                except Exception:
                    pass

                self.playwright = None

            self.logger.log(
                "Playwright stopped."
            )

            self.logger.log(
                "Browser closed successfully."
            )