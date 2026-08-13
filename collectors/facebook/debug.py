from pathlib import Path


class FacebookDebugger:

    def __init__(self, page, config):

        self.page = page

        self.config = config

        self.config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        self.config.HTML_DIR.mkdir(parents=True, exist_ok=True)

    def save_page_screenshot(self):

        path = self.config.SCREENSHOT_DIR / "facebook_page.png"

        self.page.screenshot(
            path=str(path),
            full_page=True
        )

        print(f"Screenshot saved -> {path}")

    def save_page_html(self):

        path = self.config.HTML_DIR / "page.html"

        path.write_text(
            self.page.content(),
            encoding="utf-8"
        )

        print(f"HTML saved -> {path}")

    def save_first_post_html(self, post):

        path = self.config.HTML_DIR / "first_post.html"

        path.write_text(
            post.inner_html(),
            encoding="utf-8"
        )

        print(f"First post HTML saved -> {path}")