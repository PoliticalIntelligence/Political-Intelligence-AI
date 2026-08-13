from playwright.sync_api import Locator


class TimestampParser:
    """
    Extracts the visible timestamp from a Facebook post.

    Examples:
        2m
        5h
        Yesterday
        June 20
        June 20 at 8:35 PM
    """

    LINK_SELECTOR = (
        "a[href*='/posts/'],"
        "a[href*='/videos/'],"
        "a[href*='/reel/'],"
        "a[href*='/photo/'],"
        "a[href*='story_fbid='],"
        "a[href*='permalink']"
    )

    MAX_TIMESTAMP_LENGTH = 40

    def extract(self, container: Locator) -> str:
        """
        Returns the first visible timestamp associated
        with the post permalink.
        """

        try:

            links = container.locator(self.LINK_SELECTOR)

            total = links.count()

            for i in range(total):

                try:

                    link = links.nth(i)

                    text = (
                        link
                        .inner_text(timeout=500)
                        .strip()
                    )

                    if not text:
                        continue

                    if len(text) > self.MAX_TIMESTAMP_LENGTH:
                        continue

                    return text

                except Exception:
                    continue

        except Exception:
            pass

        return ""