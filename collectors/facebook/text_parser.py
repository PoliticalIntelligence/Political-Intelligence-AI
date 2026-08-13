from playwright.sync_api import Locator
import time


class TextParser:
    """
    Extracts complete Facebook post captions.

    Priority:
    1. Expands "See more"
    2. Reads story_message
    3. Reads data-ad-preview
    4. Reads largest text block
    """

    TEXT_SELECTORS = [
        "[data-ad-rendering-role='story_message']",
        "[data-ad-preview='message']",
        "div[dir='auto']",
    ]

    REMOVE_TEXT = [
        "See more",
        "See More",
        "See less",
        "Most relevant",
        "Like",
        "Comment",
        "Share",
        "और देखें",
        "और अधिक",
    ]

    def extract(self, container: Locator) -> str:

        # --------------------------------------------------
        # Expand "See more"
        # --------------------------------------------------

        see_more_texts = [
            "See more",
            "See More",
            "और देखें",
            "और अधिक",
        ]

        for text in see_more_texts:
            try:
                button = container.get_by_text(text, exact=False).first

                if button.count() > 0 and button.is_visible():
                    button.click(timeout=1500)
                    time.sleep(0.5)
                    break

            except Exception:
                pass

        # --------------------------------------------------
        # Collect captions
        # --------------------------------------------------

        candidates = []

        for selector in self.TEXT_SELECTORS:

            try:

                locators = container.locator(selector)

                total = locators.count()

                for i in range(total):

                    node = locators.nth(i)

                    text = node.inner_text(timeout=2000)

                    text = self.clean(text)

                    if len(text) > 20:
                        candidates.append(text)

            except Exception:
                continue

        # --------------------------------------------------
        # No caption found
        # --------------------------------------------------

        if not candidates:
            return ""

        # --------------------------------------------------
        # Return longest caption
        # --------------------------------------------------

        caption = max(candidates, key=len)

        print()
        print("=" * 60)
        print("FULL CAPTION")
        print("=" * 60)
        print(caption)
        print("=" * 60)

        return caption

    # --------------------------------------------------
    # Clean text
    # --------------------------------------------------

    def clean(self, text: str) -> str:

        if not text:
            return ""

        for word in self.REMOVE_TEXT:
            text = text.replace(word, "")

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()