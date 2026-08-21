import os
import sys

from playwright.sync_api import sync_playwright
from core.config import Config


class BrowserManager:
    """
    Manages the Playwright browser lifecycle.

    Compatible with the existing FacebookCollector, which expects:
        browser_manager.create_context()
    """

    def __init__(self, logger):
        self.logger = logger
        self.playwright = None
        self.browser = None

    # ----------------------------------------------------
    # HEADLESS MODE
    # ----------------------------------------------------

    def get_headless_mode(self):
        """
        Local Windows:
            Uses Config.HEADLESS

        GitHub Actions / Linux without DISPLAY:
            Automatically uses headless=True
        """

        explicit = os.getenv("PLAYWRIGHT_HEADLESS")

        if explicit is not None:
            return explicit.lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

        if os.getenv("GITHUB_ACTIONS") == "true":
            return True

        if (
            sys.platform.startswith("linux")
            and not os.getenv("DISPLAY")
        ):
            return True

        return Config.HEADLESS

    # ----------------------------------------------------
    # START BROWSER
    # ----------------------------------------------------

    def start(self):

        self.logger.log("=" * 70)
        self.logger.log("STARTING PLAYWRIGHT")
        self.logger.log("=" * 70)

        self.logger.log(
            "Starting Playwright..."
        )

        self.playwright = sync_playwright().start()

        headless = self.get_headless_mode()

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

                slow_mo=Config.SLOW_MO,

                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-notifications",
                    "--disable-popup-blocking",
                    "--disable-infobars",
                    "--start-maximized",
                ],
            )
        )

        self.logger.log(
            "Chromium launched successfully."
        )

        return self.browser

    # ----------------------------------------------------
    # CREATE CONTEXT
    # ----------------------------------------------------
    # IMPORTANT:
    # FacebookCollector calls this exact method.
    # Do NOT rename it to new_context().
    # ----------------------------------------------------

    def create_context(self):

        self.logger.log(
            "Creating browser context..."
        )

        context = self.browser.new_context(

            viewport=Config.VIEWPORT,

            locale="en-US",

            timezone_id="Asia/Kolkata",

            java_script_enabled=True,

            ignore_https_errors=True,

            bypass_csp=True,

            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 "
                "Safari/537.36"
            ),
        )

        context.set_default_timeout(
            Config.DEFAULT_TIMEOUT
        )

        context.set_default_navigation_timeout(
            Config.DEFAULT_TIMEOUT
        )

        # Reduce automation fingerprints
        context.add_init_script(
            """
            Object.defineProperty(
                navigator,
                'webdriver',
                {
                    get: () => undefined
                }
            );

            Object.defineProperty(
                navigator,
                'platform',
                {
                    get: () => 'Win32'
                }
            );

            Object.defineProperty(
                navigator,
                'language',
                {
                    get: () => 'en-US'
                }
            );

            Object.defineProperty(
                navigator,
                'languages',
                {
                    get: () => ['en-US', 'en']
                }
            );
            """
        )

        self.logger.log(
            "Browser context created."
        )

        return context

    # ----------------------------------------------------
    # CLOSE
    # ----------------------------------------------------

    def close(self):

        self.logger.log(
            "Closing browser..."
        )

        try:

            if self.browser:

                self.browser.close()

                self.logger.log(
                    "Chromium closed."
                )

        except Exception as e:

            self.logger.log(
                f"Error closing browser: {e}"
            )

        try:

            if self.playwright:

                self.playwright.stop()

                self.logger.log(
                    "Playwright stopped."
                )

        except Exception as e:

            self.logger.log(
                f"Error stopping Playwright: {e}"
            )

        self.logger.log(
            "Browser closed successfully."
        )