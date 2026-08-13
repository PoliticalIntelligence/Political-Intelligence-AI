import csv
import os


class CSVExporter:
    """
    Export Facebook posts to CSV.
    """

    def __init__(self, output_dir="output"):

        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------------------------------

    def export(self, posts, filename="posts.csv"):

        filepath = os.path.join(
            self.output_dir,
            filename
        )

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as csvfile:

            writer = csv.writer(csvfile)

            # -------------------------------------------------
            # Headers
            # -------------------------------------------------

            writer.writerow([

                "Author",

                "Timestamp",

                "Post URL",

                "Post Text",

                "Reactions",

                "Comments",

                "Shares",

                "Like",

                "Love",

                "Care",

                "Haha",

                "Wow",

                "Sad",

                "Angry",

                "Images",

                "Videos",

                "Scraped At",

                "Source Page"

            ])

            # -------------------------------------------------
            # Data
            # -------------------------------------------------

            for post in posts:

                writer.writerow([

                    post.author,

                    post.timestamp,

                    post.url,

                    post.text,

                    post.reactions,

                    post.comments,

                    post.shares,

                    post.like,

                    post.love,

                    post.care,

                    post.haha,

                    post.wow,

                    post.sad,

                    post.angry,

                    "\n".join(post.images),

                    "\n".join(post.videos),

                    post.scraped_at,

                    post.source_page

                ])

        print("\n==============================")
        print("CSV EXPORT")
        print("==============================")
        print(f"Posts Exported : {len(posts)}")
        print(f"Saved To       : {filepath}")
        print("==============================")