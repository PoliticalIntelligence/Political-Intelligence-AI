from pathlib import Path

from models.facebook_post import FacebookPost

from collectors.facebook.timestamp_parser import TimestampParser
from collectors.facebook.see_more import SeeMoreExpander
from collectors.facebook.text_parser import TextParser
from collectors.facebook.media_parser import MediaParser
from collectors.facebook.url_parser import URLParser


class PostParser:
    """
    Parses a single Facebook post.

    Pipeline
    --------
    Expand Post
            ↓
    Extract Page Name
            ↓
    Extract Timestamp
            ↓
    Extract Caption
            ↓
    Extract Media
            ↓
    Extract URL
            ↓
    Return FacebookPost
    """

    def __init__(self, page):

        self.page = page

        self.timestamp_parser = TimestampParser()
        self.see_more = SeeMoreExpander()
        self.text_parser = TextParser()
        self.media_parser = MediaParser()
        self.url_parser = URLParser()

    # ----------------------------------------------------
    # Page Name
    # ----------------------------------------------------

    def extract_page_name(self, container):

        selectors = [

            "[data-ad-rendering-role='profile_name']",

            "h2",

            "h3",

            "strong",

            "a[role='link'] span",

            "a[role='link']"

        ]

        ignore = {

            "Like",
            "Comment",
            "Share",
            "Reply",
            "Follow",
            "Send message",
            "Message",
            "See more",
            "See less"

        }

        for selector in selectors:

            try:

                nodes = container.locator(selector)

                total = nodes.count()

                for i in range(total):

                    text = nodes.nth(i).inner_text(
                        timeout=500
                    ).strip()

                    text = " ".join(text.split())

                    if not text:
                        continue

                    if text in ignore:
                        continue

                    if len(text) < 2:
                        continue

                    if len(text) > 80:
                        continue

                    return text

            except Exception:

                continue

        return "Unknown"

    # ----------------------------------------------------
    # Timestamp
    # ----------------------------------------------------

    def extract_timestamp(self, container):

        return self.timestamp_parser.extract(container)

    # ----------------------------------------------------
    # Save Expanded HTML
    # ----------------------------------------------------

    def save_html(self, container):

        try:

            html = container.inner_html()

            output = Path("debug")

            output.mkdir(exist_ok=True)

            with open(
                output / "expanded_post.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(html)

        except Exception:

            pass

    # ----------------------------------------------------
    # Parse
    # ----------------------------------------------------

    def parse(self, container):

        # Expand caption first

        self.see_more.expand(container)

        # Save HTML for debugging

        self.save_html(container)

        # -------- Basic Information --------

        page_name = self.extract_page_name(container)

        published = self.extract_timestamp(container)

        # -------- Caption --------

        caption = self.text_parser.extract(container)

        # -------- Media --------

        media = self.media_parser.extract(container)

        # -------- URL --------

        post_url = self.url_parser.extract(container)

        # Remaining implementation continues in Part 2...
        # ----------------------------------------------------
        # Build FacebookPost
        # ----------------------------------------------------

        post = FacebookPost(

            leader_name=page_name,

            page_name=page_name,

            post_text=caption,

            post_url=post_url,

            published_at=published,

            likes=0,

            comments=0,

            shares=0,

            images=media["images"],

            videos=media["videos"],

            is_video=media["is_video"],

            is_reel=media["is_reel"],

            is_live=False

        )

        # ----------------------------------------------------
        # Debug
        # ----------------------------------------------------

        print()

        print("=" * 80)
        print("FACEBOOK POST")
        print("=" * 80)

        print(f"Page Name   : {post.page_name}")

        print(f"Published   : {post.published_at}")

        print(f"URL         : {post.post_url}")

        print(f"Video       : {post.is_video}")

        print(f"Reel        : {post.is_reel}")

        print(f"Images      : {len(post.images)}")

        print(f"Videos      : {len(post.videos)}")

        print()

        print("-" * 80)

        if post.post_text:

            print(post.post_text)

        else:

            print("[No Caption Found]")

        print("-" * 80)

        if post.images:

            print()

            print("IMAGE URLS")

            print()

            for img in post.images:

                print(img)

        if post.videos:

            print()

            print("VIDEO URLS")

            print()

            for video in post.videos:

                print(video)

        print("=" * 80)

        return post