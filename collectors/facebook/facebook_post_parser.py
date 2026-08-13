from datetime import datetime
import os

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from models.post import Post

from collectors.facebook.text_parser import TextParser
from collectors.facebook.url_parser import URLParser
from collectors.facebook.media_parser import MediaParser
from collectors.facebook.timestamp_parser import TimestampParser
from collectors.facebook.engagement_parser import EngagementParser
from collectors.facebook.author_parser import AuthorParser


class FacebookPostParser:
    """
    Master parser responsible for converting a Facebook post
    container into a Post object.
    """

    LOADING_SELECTOR = "[aria-label='Loading...']"

    READY_SELECTORS = [

        "[data-ad-rendering-role='profile_name']",
        "[data-ad-rendering-role='story_message']",
        "[aria-label='See who reacted to this']",

        "video",

        "img[data-imgperflogname]",

        "a[href*='/posts/']",
        "a[href*='/videos/']",
        "a[href*='/reel/']",
        "a[href*='story_fbid=']",
        "a[href*='permalink']",

    ]

    def __init__(self):

        self.author_parser = AuthorParser()
        self.text_parser = TextParser()
        self.url_parser = URLParser()
        self.media_parser = MediaParser()
        self.timestamp_parser = TimestampParser()
        self.engagement_parser = EngagementParser()

        self.debug_saved = False

    # ---------------------------------------------------------
    # Fast URL extraction
    # ---------------------------------------------------------

    def extract_url(self, container):

        try:
            return self.url_parser.extract(container)

        except Exception as e:

            print(f"[URL Parser] {e}")

            return ""

    # ---------------------------------------------------------
    # Wait until Facebook finishes rendering
    # ---------------------------------------------------------

    def wait_until_ready(
        self,
        container,
        timeout=8000
    ):

        try:

            loading = container.locator(
                self.LOADING_SELECTOR
            )

            if loading.count():

                loading.first.wait_for(
                    state="hidden",
                    timeout=timeout
                )

        except Exception:
            pass

        for selector in self.READY_SELECTORS:

            try:

                locator = container.locator(selector)

                if locator.count() == 0:
                    continue

                locator.first.wait_for(
                    state="visible",
                    timeout=timeout
                )

                return

            except PlaywrightTimeoutError:
                continue

            except Exception:
                continue

    # ---------------------------------------------------------
    # Save debug files (only once)
    # ---------------------------------------------------------

    def save_debug_html(self, container):

        if self.debug_saved:
            return

        try:

            with open(
                "debug_container.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    container.evaluate(
                        "el => el.outerHTML"
                    )
                )

            with open(
                "debug_page.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    container.page.content()
                )

            self.debug_saved = True

        except Exception as e:

            print(f"[DEBUG] {e}")


    # ---------------------------------------------------------
    # Parse Complete Post
    # ---------------------------------------------------------

    def parse(
        self,
        container,
        source_page: str = ""
    ) -> Post:

        # ---------------------------------------------
        # Wait until Facebook has finished rendering
        # ---------------------------------------------

        self.wait_until_ready(container)

        # ---------------------------------------------
        # Create Post model
        # ---------------------------------------------

        post = Post()

        # ---------------------------------------------
        # Save debug once
        # ---------------------------------------------

        self.save_debug_html(container)

        # ---------------------------------------------
        # URL
        # ---------------------------------------------

        try:

            post.url = self.extract_url(container)

        except Exception as e:

            print(f"[URL Parser] {e}")

            post.url = ""

        # ---------------------------------------------
        # Author
        # ---------------------------------------------

        try:

            post.author = self.author_parser.extract(container)

        except Exception as e:

            print(f"[Author Parser] {e}")

            post.author = ""

        # ---------------------------------------------
        # Caption
        # ---------------------------------------------

        try:

            post.text = self.text_parser.extract(container)

        except Exception as e:

            print(f"[Text Parser] {e}")

            post.text = ""

        # ---------------------------------------------
        # Timestamp
        # ---------------------------------------------

        try:

            post.timestamp = self.timestamp_parser.extract(
                container
            )

        except Exception as e:

            print(f"[Timestamp Parser] {e}")

            post.timestamp = ""

        # ---------------------------------------------
        # Media
        # ---------------------------------------------

        try:

            media = self.media_parser.extract(container)

            if isinstance(media, dict):

                post.images = media.get(
                    "images",
                    []
                )

                post.videos = media.get(
                    "videos",
                    []
                )

            elif isinstance(media, list):

                post.images = media
                post.videos = []

            else:

                post.images = []
                post.videos = []

        except Exception as e:

            print(f"[Media Parser] {e}")

            post.images = []
            post.videos = []
        # ---------------------------------------------
        # Engagement
        # ---------------------------------------------

        try:

            engagement = self.engagement_parser.extract(
                container
            )

            post.reactions = engagement.get(
                "reactions",
                0
            )

            post.comments = engagement.get(
                "comments",
                0
            )

            post.shares = engagement.get(
                "shares",
                0
            )

            post.like = engagement.get(
                "like",
                0
            )

            post.love = engagement.get(
                "love",
                0
            )

            post.care = engagement.get(
                "care",
                0
            )

            post.haha = engagement.get(
                "haha",
                0
            )

            post.wow = engagement.get(
                "wow",
                0
            )

            post.sad = engagement.get(
                "sad",
                0
            )

            post.angry = engagement.get(
                "angry",
                0
            )

        except Exception as e:

            print(f"[Engagement Parser] {e}")

            post.reactions = 0
            post.comments = 0
            post.shares = 0

            post.like = 0
            post.love = 0
            post.care = 0
            post.haha = 0
            post.wow = 0
            post.sad = 0
            post.angry = 0

        # ---------------------------------------------
        # Metadata
        # ---------------------------------------------

        post.scraped_at = datetime.now().isoformat()
        post.source_page = source_page

        # ---------------------------------------------
        # Debug Summary
        # ---------------------------------------------

        print()
        print("=" * 80)
        print("POST PARSED")
        print("=" * 80)

        print(f"Author     : {getattr(post, 'author', '')}")
        print(f"URL        : {post.url}")
        print(f"Timestamp  : {post.timestamp}")

        if hasattr(post, "text") and post.text:

            preview = post.text.replace("\n", " ")

            if len(preview) > 100:
                preview = preview[:100] + "..."

            print(f"Text       : {preview}")

        print(f"Images     : {len(post.images)}")
        print(f"Videos     : {len(post.videos)}")
        print(f"Reactions  : {post.reactions}")
        print(f"Comments   : {post.comments}")
        print(f"Shares     : {post.shares}")

        print(
            f"Like:{post.like} "
            f"Love:{post.love} "
            f"Care:{post.care} "
            f"Haha:{post.haha} "
            f"Wow:{post.wow} "
            f"Sad:{post.sad} "
            f"Angry:{post.angry}"
        )

        print("=" * 80)

        return post


