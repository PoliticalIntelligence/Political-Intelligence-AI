import time
from datetime import datetime, timedelta
from typing import List, Set, Optional

from playwright.sync_api import Page

from collectors.facebook.container_collector import ContainerCollector
from collectors.facebook.facebook_post_parser import FacebookPostParser
from collectors.facebook.facebook_date_parser import FacebookDateParser

from models.post import Post


class HistoricalFacebookCrawler:
    """
    Historical Facebook crawler.

    Scrapes posts until the configured history window
    (default: 45 days) has been reached.
    """

    # Safety limit
    MAX_SCROLLS = 9999

    # Wait after each scroll
    SCROLL_PAUSE = 2

    def __init__(
        self,
        page: Page,
        history_days: int = 45,
    ):

        self.page = page

        self.collector = ContainerCollector(page)

        self.post_parser = FacebookPostParser()

        self.date_parser = FacebookDateParser()

        self.history_days = history_days

        self.cutoff_date = (
            datetime.now() - timedelta(days=history_days)
        )

        self.posts: List[Post] = []

        self.seen_urls: Set[str] = set()

        self.scrolls = 0

        self.stop_crawling = False

    # ----------------------------------------------------
    # Page Height
    # ----------------------------------------------------

    def page_height(self) -> int:

        try:

            return self.page.evaluate(
                "document.body.scrollHeight"
            )

        except Exception:

            return 0

    # ----------------------------------------------------
    # Scroll Once
    # ----------------------------------------------------

    def scroll_once(self):

        print()
        print("=" * 70)
        print(f"SCROLL #{self.scrolls + 1}")
        print("=" * 70)

        self.page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        time.sleep(self.SCROLL_PAUSE)

        self.scrolls += 1

    # ----------------------------------------------------
    # Collect Visible Containers
    # ----------------------------------------------------

    def collect_post_containers(self):

        try:

            containers = (
                self.collector.get_post_containers()
            )

            print(
                f"Visible Containers : {len(containers)}"
            )

            return containers

        except Exception as e:

            print(f"[Collector Error] {e}")

            return []

    # ----------------------------------------------------
    # Parse Timestamp
    # ----------------------------------------------------

    def parse_post_date(
        self,
        timestamp_text: str
    ) -> Optional[datetime]:

        try:

            return self.date_parser.parse(
                timestamp_text
            )

        except Exception as e:

            print(
                f"[Date Parser] {timestamp_text} -> {e}"
            )

            return None

    # ----------------------------------------------------
    # Check History Window
    # ----------------------------------------------------

    def is_recent(
        self,
        post_date: datetime
    ) -> bool:

        return post_date >= self.cutoff_date
    # ----------------------------------------------------
    # Parse One Container
    # ----------------------------------------------------

    def parse_container(
        self,
        container
    ) -> Optional[Post]:

        try:

            # ------------------------------------------
            # Extract URL first
            # ------------------------------------------

            url = self.post_parser.extract_url(container)

            if not url:
                return None

            # Skip duplicates

            if url in self.seen_urls:
                return None

            # ------------------------------------------
            # Parse complete post
            # ------------------------------------------

            post = self.post_parser.parse(
                container,
                source_page=self.page.url
            )

            if post is None:
                return None

            if not post.url:
                return None

            # Mark URL as processed

            self.seen_urls.add(post.url)

            # ------------------------------------------
            # Parse timestamp
            # ------------------------------------------

            post_date = self.parse_post_date(
                post.timestamp
            )

            print()
            print("-" * 70)
            print(f"Timestamp : {post.timestamp}")
            print(f"Parsed    : {post_date}")
            print("-" * 70)

            # ------------------------------------------
            # Parser failed
            # ------------------------------------------

            if post_date is None:

                print(
                    f"[WARNING] Could not parse timestamp: {post.timestamp}"
                )

                # Keep the post instead of discarding it

                return post

            # ------------------------------------------
            # Older than cutoff?
            # ------------------------------------------

            if not self.is_recent(post_date):

                print()
                print("=" * 70)
                print("HISTORICAL LIMIT REACHED")
                print("=" * 70)

                print(
                    f"Cutoff Date : {self.cutoff_date.strftime('%d %b %Y %H:%M')}"
                )

                print(
                    f"Post Date   : {post_date.strftime('%d %b %Y %H:%M')}"
                )

                print()

                print(
                    "Stopping after finishing current visible batch..."
                )

                # Don't stop immediately.
                # Let crawl() finish processing the
                # currently visible containers.

                self.stop_crawling = True

                return None

            # ------------------------------------------
            # Valid post
            # ------------------------------------------

            return post

        except Exception as e:

            print()

            print("=" * 70)
            print("PARSE CONTAINER ERROR")
            print("=" * 70)

            print(e)

            return None

    # ----------------------------------------------------
    # Progress
    # ----------------------------------------------------

    def print_progress(self):

        print()
        print("=" * 70)
        print("HISTORICAL SCRAPER STATUS")
        print("=" * 70)

        print(f"Scrolls         : {self.scrolls}")
        print(f"Collected Posts : {len(self.posts)}")
        print(f"Unique URLs     : {len(self.seen_urls)}")
        print(f"History Window  : {self.history_days} Days")
        print(
            f"Cutoff Date     : {self.cutoff_date.strftime('%d %b %Y')}"
        )

        print("=" * 70)

    # ----------------------------------------------------
    # End Of Page
    # ----------------------------------------------------

    def reached_end(
        self,
        previous_height,
        current_height,
    ):

        if current_height == previous_height:

            print()
            print("=" * 70)
            print("END OF FACEBOOK PAGE")
            print("=" * 70)

            return True

        return False

    # ----------------------------------------------------
    # Crawl
    # ----------------------------------------------------

    def crawl(self):

        print()
        print("=" * 70)
        print("HISTORICAL FACEBOOK CRAWLER")
        print("=" * 70)

        self.posts = []
        self.seen_urls = set()
        self.scrolls = 0
        self.stop_crawling = False

        previous_height = self.page_height()

        while True:

            print()
            print("=" * 70)
            print(f"PASS #{self.scrolls + 1}")
            print("=" * 70)

            containers = self.collect_post_containers()

            print(f"Scanning {len(containers)} containers...")

            new_posts = 0

            # ------------------------------------------
            # Parse all visible posts
            # ------------------------------------------

            for container in containers:

                post = self.parse_container(container)

                if post is None:
                    continue

                self.posts.append(post)

                new_posts += 1

                print()

                print(
                    f"[{len(self.posts)}] {post.timestamp}"
                )

                if getattr(post, "text", None):

                    preview = post.text.replace(
                        "\n",
                        " "
                    )

                    if len(preview) > 80:

                        preview = preview[:80] + "..."

                    print(preview)

                print(post.url)

            self.print_progress()

            # ------------------------------------------
            # Finish current batch then stop
            # ------------------------------------------

            if self.stop_crawling:

                print()
                print("=" * 70)
                print("45 DAY HISTORY REACHED")
                print("=" * 70)

                break

            # ------------------------------------------
            # Scroll
            # ------------------------------------------

            self.scroll_once()

            current_height = self.page_height()

            if self.reached_end(
                previous_height,
                current_height,
            ):
                break

            previous_height = current_height

            # ------------------------------------------
            # Safety Limit
            # ------------------------------------------

            if self.scrolls >= self.MAX_SCROLLS:

                print()
                print("=" * 70)
                print("MAXIMUM SCROLL LIMIT REACHED")
                print("=" * 70)

                break

        print()
        print("=" * 70)
        print("HISTORICAL CRAWL COMPLETE")
        print("=" * 70)

        print(
            f"Total Posts : {len(self.posts)}"
        )

        return self.posts

    # ----------------------------------------------------
    # Statistics
    # ----------------------------------------------------

    def statistics(self):

        print()
        print("=" * 70)
        print("HISTORICAL SCRAPE SUMMARY")
        print("=" * 70)

        print(
            f"History Window : {self.history_days} Days"
        )

        print(
            f"Cutoff Date    : {self.cutoff_date.strftime('%Y-%m-%d')}"
        )

        print(
            f"Total Scrolls  : {self.scrolls}"
        )

        print(
            f"Posts Collected: {len(self.posts)}"
        )

        print(
            f"Unique URLs    : {len(self.seen_urls)}"
        )

        if self.posts:

            print(
                f"Newest Post    : {self.posts[0].timestamp}"
            )

            print(
                f"Oldest Post    : {self.posts[-1].timestamp}"
            )

        print("=" * 70)

    # ----------------------------------------------------
    # Get Posts
    # ----------------------------------------------------

    def get_posts(self):

        return self.posts

    # ----------------------------------------------------
    # Reset
    # ----------------------------------------------------

    def reset(self):

        self.posts = []
        self.seen_urls.clear()
        self.scrolls = 0
        self.stop_crawling = False

    # ----------------------------------------------------
    # Run
    # ----------------------------------------------------

    def run(self):

        self.reset()

        posts = self.crawl()

        self.statistics()

        return posts

