import re
from html import escape


class EngagementParser:
    """
    Facebook Engagement Parser

    Extracts:
    - Total reactions
    - Reaction breakdown
    - Comments
    - Shares

    (Comments & Shares parser will be added in Part 2)
    """

    REACTION_TYPES = {
        "Like": "like",
        "Love": "love",
        "Care": "care",
        "Haha": "haha",
        "Wow": "wow",
        "Sad": "sad",
        "Angry": "angry",
    }

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Number Parser
    # ---------------------------------------------------------

    def parse_number(self, value):

        if not value:
            return 0

        value = (
            str(value)
            .strip()
            .replace(",", "")
            .upper()
        )

        try:

            if value.endswith("K"):
                return int(float(value[:-1]) * 1000)

            if value.endswith("M"):
                return int(float(value[:-1]) * 1000000)

            if value.endswith("B"):
                return int(float(value[:-1]) * 1000000000)

            return int(float(value))

        except Exception:

            return 0

    # ---------------------------------------------------------
    # Save Complete HTML
    # ---------------------------------------------------------

    def save_debug_html(self, container):

        """
        Saves the complete HTML of the current Facebook post.

        This file will be uploaded later so the parser
        can be rewritten against the real Facebook DOM.
        """

        try:

            html = container.evaluate(
                "el => el.outerHTML"
            )

            with open(
                "ENGAGEMENT_DEBUG.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(html)

            print("=" * 70)
            print("ENGAGEMENT_DEBUG.html SAVED")
            print("=" * 70)

        except Exception as e:

            print(e)

    # ---------------------------------------------------------
    # Total Reactions
    # ---------------------------------------------------------

    def extract_total_reactions(self, container):

        selectors = [

            "[aria-label='See who reacted to this']",

            "[aria-label*='reacted']",

            "[aria-label*='reaction']",

            "[aria-label*='Like:']",

            "[role='button'][aria-label*='Like']",

        ]

        for selector in selectors:

            try:

                nodes = container.locator(selector)

                total = nodes.count()

                for i in range(total):

                    node = nodes.nth(i)

                    values = []

                    try:
                        text = node.inner_text(timeout=500)

                        if text:
                            values.append(text)

                    except Exception:
                        pass

                    try:
                        aria = node.get_attribute(
                            "aria-label"
                        )

                        if aria:
                            values.append(aria)

                    except Exception:
                        pass

                    for value in values:

                        match = re.search(
                            r"([0-9]+(?:\.[0-9]+)?[KMB]?)",
                            value
                        )

                        if not match:
                            continue

                        return self.parse_number(
                            match.group(1)
                        )

            except Exception:

                continue

        return 0

    # ---------------------------------------------------------
    # Reaction Breakdown
    # ---------------------------------------------------------

    def extract_reaction_breakdown(self, container):

        reactions = {

            "like": 0,
            "love": 0,
            "care": 0,
            "haha": 0,
            "wow": 0,
            "sad": 0,
            "angry": 0,

        }

        try:

            nodes = container.locator(
                "[aria-label]"
            )

            total = nodes.count()

            for i in range(total):

                try:

                    label = nodes.nth(i).get_attribute(
                        "aria-label"
                    )

                    if not label:
                        continue

                    for fb_name, key in self.REACTION_TYPES.items():

                        if not label.startswith(
                            fb_name + ":"
                        ):
                            continue

                        match = re.search(
                            r"([0-9]+(?:\.[0-9]+)?[KMB]?)",
                            label
                        )

                        if not match:
                            continue

                        reactions[key] = self.parse_number(
                            match.group(1)
                        )

                except Exception:

                    continue

        except Exception:

            pass

        return reactions
    # ---------------------------------------------------------
    # Generic Metric Extractor
    # ---------------------------------------------------------

    def extract_metric(self, container, keywords):

        try:

            nodes = container.locator("*")

            total = nodes.count()

            for i in range(total):

                node = nodes.nth(i)

                texts = []

                try:
                    text = node.inner_text(timeout=100).strip()
                    if text:
                        texts.append(text)
                except Exception:
                    pass

                try:
                    aria = node.get_attribute("aria-label")
                    if aria:
                        texts.append(aria)
                except Exception:
                    pass

                for value in texts:

                    lower = value.lower()

                    if not any(
                        keyword in lower
                        for keyword in keywords
                    ):
                        continue

                    match = re.search(
                        r"([0-9]+(?:\.[0-9]+)?[KMB]?)",
                        value
                    )

                    if match:

                        return self.parse_number(
                            match.group(1)
                        )

        except Exception:
            pass

        return 0

    # ---------------------------------------------------------
    # Comments
    # ---------------------------------------------------------

    def extract_comments(self, container):

        return self.extract_metric(

            container,

            [

                "comment",

                "comments",

                "reply",

                "replies"

            ]

        )

    # ---------------------------------------------------------
    # Shares
    # ---------------------------------------------------------

    def extract_shares(self, container):

        return self.extract_metric(

            container,

            [

                "share",

                "shares",

                "shared"

            ]

        )

    # ---------------------------------------------------------
    # Main Extract
    # ---------------------------------------------------------

    def extract(self, container):

        # Save HTML once for analysis
        self.save_debug_html(container)

        reactions = self.extract_reaction_breakdown(
            container
        )

        total_reactions = self.extract_total_reactions(
            container
        )

        comments = self.extract_comments(
            container
        )

        shares = self.extract_shares(
            container
        )

        print("\n" + "=" * 70)
        print("ENGAGEMENT")
        print("=" * 70)
        print(f"Reactions : {total_reactions}")
        print(f"Comments  : {comments}")
        print(f"Shares    : {shares}")
        print("=" * 70)

        return {

            "reactions": total_reactions,

            "comments": comments,

            "shares": shares,

            **reactions

        }


