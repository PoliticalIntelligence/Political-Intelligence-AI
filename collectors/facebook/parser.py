from typing import List
import time

from collectors.facebook.post_parser import PostParser
from collectors.facebook.debug import FacebookDebugger
from collectors.facebook.container_collector import ContainerCollector

from core.config import Config
from models.facebook_post import FacebookPost


class FacebookParser:

    def __init__(self, page):

        self.page = page

        self.post_parser = PostParser(page)

        self.debugger = FacebookDebugger(page, Config)

        self.collector = ContainerCollector(page)

    # ----------------------------------------------------
    # Auto Scroll
    # ----------------------------------------------------

    def auto_scroll(
        self,
        max_scrolls: int = 8,
        pause: float = 2.0
    ):

        print("\nScrolling page...\n")

        last_height = 0

        for i in range(max_scrolls):

            self.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )

            time.sleep(pause)

            height = self.page.evaluate(
                "document.body.scrollHeight"
            )

            print(
                f"Scroll {i+1}/{max_scrolls}  Height={height}"
            )

            if height == last_height:

                print("Reached end of loaded content.")

                break

            last_height = height

    # ----------------------------------------------------
    # Main
    # ----------------------------------------------------

    def get_posts(
        self,
        limit: int = 5
    ) -> List[FacebookPost]:

        self.auto_scroll()

        print("\nCollecting post containers...")

        containers = self.collector.get_post_containers()

        print(
            f"\nCollected {len(containers)} post containers."
        )

        self.debugger.save_page_screenshot()

        self.debugger.save_page_html()

        if containers:

            self.debugger.save_first_post_html(
                containers[0]
            )

        posts = []

        for container in containers:

            if len(posts) >= limit:

                break

            try:

                post = self.post_parser.parse(container)

                posts.append(post)

            except Exception as e:

                print()

                print("Failed parsing post")

                print(e)

        print()

        print("=" * 70)
        print(f"TOTAL POSTS : {len(posts)}")
        print("=" * 70)

        return posts