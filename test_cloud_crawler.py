"""
CONTROLLED CLOUD-STATE CRAWLER TEST

Purpose:
- Tests BrowserManager + FacebookCrawler + new Google-Sheets-backed ScraperState.
- Uses ONE Facebook page only.
- Does NOT run AI.
- Does NOT write to Raw_Posts or AI Analysis.
- Limits crawling to 5 scrolls for a safe test.

Run from project root:
    python test_cloud_crawler.py
"""

from browser.browser_manager import BrowserManager
from collectors.facebook.crawler import FacebookCrawler
from utils.logger import Logger


TEST_PAGE = "https://www.facebook.com/DoodhRam"


class LimitedFacebookCrawler(FacebookCrawler):
    MAX_SCROLLS = 5
    SCROLL_PAUSE = 2


def main():
    logger = Logger()
    browser = None
    context = None
    page = None

    print("=" * 70)
    print("CONTROLLED CLOUD-STATE CRAWLER TEST")
    print("=" * 70)
    print(f"Test page : {TEST_PAGE}")
    print("AI        : OFF")
    print("Sheet     : READ ONLY")
    print("Max scrolls: 5")
    print("=" * 70)

    try:
        browser = BrowserManager(logger)
        browser.start()

        context = browser.create_context()
        page = context.new_page()

        print("\nOpening Facebook page...")
        page.goto(
            TEST_PAGE,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print(f"Page title: {page.title()}")
        print(f"Page URL  : {page.url}")

        crawler = LimitedFacebookCrawler(page)

        posts = crawler.crawl()

        print("\n" + "=" * 70)
        print("TEST RESULT")
        print("=" * 70)
        print(f"New posts detected: {len(posts)}")

        if len(posts) == 0:
            print(
                "\nRESULT: PASS candidate - no new posts were detected "
                "before the crawler hit the existing-post stop condition "
                "or the page/end limit."
            )
        else:
            print(
                "\nRESULT: CRAWLER FOUND NEW POSTS."
                "\nThis is not a failure. It means the selected page has "
                "posts that are not currently in Raw_Posts."
            )

        for index, post in enumerate(posts[:10], start=1):
            print(f"{index}. {post.url}")

        print("=" * 70)

    except Exception as exc:
        print("\n" + "=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70)
        raise

    finally:
        try:
            if context:
                context.close()
        except Exception:
            pass

        try:
            if browser:
                browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
