import time
from typing import List, Set

from playwright.sync_api import Page

from collectors.facebook.container_collector import ContainerCollector
from collectors.facebook.facebook_post_parser import FacebookPostParser
from models.post import Post
from state.scraper_state import ScraperState


class FacebookCrawler:
    """
    Facebook crawler responsible for discovering NEW Facebook posts.

    Stops when:
    - Previously scraped post is found
    - End of page is reached
    - Maximum scroll limit is reached
    """

    MAX_SCROLLS = 30
    SCROLL_PAUSE = 2

    def __init__(self, page: Page):

        self.page = page

        self.collector = ContainerCollector(page)
        self.post_parser = FacebookPostParser()
        self.state = ScraperState()

        self.posts: List[Post] = []

        # URLs collected during this crawl
        self.current_urls: List[str] = []

        # Prevent duplicate parsing in same run
        self.seen_urls: Set[str] = set()

    # ------------------------------------------------------------
    # Page Height
    # ------------------------------------------------------------

    def page_height(self):

        try:
            return self.page.evaluate(
                "document.body.scrollHeight"
            )

        except Exception:
            return 0

    # ------------------------------------------------------------
    # Scroll Once
    # ------------------------------------------------------------

    def scroll_once(self):

        print("\nScrolling page...\n")

        self.page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        time.sleep(self.SCROLL_PAUSE)

    # ------------------------------------------------------------
    # Collect Visible Posts
    # ------------------------------------------------------------

    def collect_posts(self):

        try:

            containers = self.collector.get_post_containers()

            print(f"Visible post containers : {len(containers)}")

            return containers

        except Exception as e:

            print(f"[Collector] {e}")

            return []

    # ------------------------------------------------------------
    # Parse One Container
    # ------------------------------------------------------------

    def parse_container(self, container):

        try:

            # Fast URL extraction
            url = self.post_parser.extract_url(container)

            if not url:
                return None

            # Already parsed during this run
            if url in self.seen_urls:
                return None

            # Previously scraped
            if self.state.is_known(url):
                return "STOP"

            post = self.post_parser.parse(
                container,
                source_page=self.page.url
            )

            self.seen_urls.add(post.url)
            self.current_urls.append(post.url)

            return post

        except Exception as e:

            print(f"[Parser] {e}")

            return None

    # ------------------------------------------------------------
    # Stop Conditions
    # ------------------------------------------------------------

    def should_stop(
        self,
        last_height,
        current_height,
        scrolls
    ):

        if current_height == last_height:

            print("\nReached end of page.")

            return True

        if scrolls >= self.MAX_SCROLLS:

            print("\nReached maximum scroll limit.")

            return True

        return False

    # ------------------------------------------------------------
    # Crawl
    # ------------------------------------------------------------

    def crawl(self):

        print("\n" + "=" * 70)
        print("FACEBOOK CRAWLER")
        print("=" * 70)

        self.posts = []
        self.current_urls = []
        self.seen_urls = set()

        last_height = self.page_height()
        scrolls = 0

        while True:

            print(f"\n========== PASS {scrolls + 1} ==========\n")

            containers = self.collect_posts()

            print(f"Scanning {len(containers)} containers...\n")

            stop = False

            for container in containers:

                result = self.parse_container(container)

                if result is None:
                    continue

                if result == "STOP":

                    print("\nPreviously scraped post found.")
                    print("Stopping crawler.")

                    stop = True
                    break

                self.posts.append(result)

                print(f"[{len(self.posts)}] {result.url}")

            if stop:
                break

            self.scroll_once()

            current_height = self.page_height()

            scrolls += 1

            if self.should_stop(
                last_height,
                current_height,
                scrolls
            ):
                break

            last_height = current_height

        # ----------------------------------------------------
        # Save State
        # ----------------------------------------------------

        if self.current_urls:

            self.state.update(self.current_urls)

            print(f"\nSaved {len(self.current_urls)} URLs.")

        print("\n" + "=" * 70)
        print(f"TOTAL NEW POSTS : {len(self.posts)}")
        print("=" * 70)

        return self.posts