import json
import os


class JsonExporter:
    """
    Export Facebook posts to JSON.
    """

    def __init__(self, output_dir="output"):

        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------------------------------

    def export(self, posts, filename="posts.json"):

        filepath = os.path.join(
            self.output_dir,
            filename
        )

        data = []

        for post in posts:

            data.append({

                # -------------------------------------------------
                # Basic Information
                # -------------------------------------------------

                "url": post.url,

                "text": post.text,

                "timestamp": post.timestamp,

                "author": post.author,

                # -------------------------------------------------
                # Engagement Summary
                # -------------------------------------------------

                "reactions": post.reactions,

                "comments": post.comments,

                "shares": post.shares,

                # -------------------------------------------------
                # Reaction Breakdown
                # -------------------------------------------------

                "like": post.like,

                "love": post.love,

                "care": post.care,

                "haha": post.haha,

                "wow": post.wow,

                "sad": post.sad,

                "angry": post.angry,

                # -------------------------------------------------
                # Media
                # -------------------------------------------------

                "images": post.images,

                "videos": post.videos,

                # -------------------------------------------------
                # Metadata
                # -------------------------------------------------

                "scraped_at": post.scraped_at,

                "source_page": post.source_page

            })

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("\n==============================")
        print("JSON EXPORT")
        print("==============================")
        print(f"Posts Exported : {len(posts)}")
        print(f"Saved To       : {filepath}")
        print("==============================")