from urllib.parse import (
    urljoin,
    urlparse,
    parse_qsl,
    urlencode,
    urlunparse,
)

from playwright.sync_api import Locator


class URLParser:
    """
    Extracts the canonical Facebook post URL.

    Supported:
    - Posts
    - Videos
    - Reels
    - Photos
    - story_fbid
    - permalink

    Always returns ONE normalized URL.
    """

    BASE_URL = "https://www.facebook.com"

    LINK_SELECTOR = (
        "a[href*='/posts/'],"
        "a[href*='/videos/'],"
        "a[href*='/reel/'],"
        "a[href*='/photo/'],"
        "a[href*='story_fbid='],"
        "a[href*='permalink']"
    )

    URL_PRIORITY = [
        "/posts/",
        "story_fbid=",
        "/videos/",
        "/reel/",
        "/photo/",
        "permalink",
    ]

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def extract(self, container: Locator) -> str:

        candidates = []

        try:

            links = container.locator(self.LINK_SELECTOR)

            for i in range(links.count()):

                href = links.nth(i).get_attribute("href")

                if not href:
                    continue

                href = urljoin(self.BASE_URL, href)

                href = self.normalize(href)

                if href not in candidates:
                    candidates.append(href)

        except Exception:
            return ""

        if not candidates:
            return ""

        return self.best_candidate(candidates)

    # ---------------------------------------------------------
    # Normalize URL
    # ---------------------------------------------------------

    def normalize(self, url: str) -> str:

        parsed = urlparse(url)

        allowed = []

        for key, value in parse_qsl(parsed.query):

            if key in (
                "story_fbid",
                "fbid",
                "id",
                "v",
            ):
                allowed.append((key, value))

        query = urlencode(allowed)

        clean = parsed._replace(
            query=query,
            fragment=""
        )

        normalized = urlunparse(clean)

        normalized = normalized.rstrip("/")

        return normalized

    # ---------------------------------------------------------
    # Select Best URL
    # ---------------------------------------------------------

    def best_candidate(self, urls):

        def score(url):

            for i, pattern in enumerate(self.URL_PRIORITY):
                if pattern in url:
                    return len(self.URL_PRIORITY) - i

            return 0

        urls = sorted(
            urls,
            key=lambda x: (score(x), -len(x)),
            reverse=True,
        )

        return urls[0]