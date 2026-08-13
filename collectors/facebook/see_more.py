from playwright.sync_api import Locator
import time


class SeeMoreExpander:
    """
    Expands Facebook post captions.

    Supports:
    ----------
    ✓ See more
    ✓ ... More
    ✓ More
    ✓ Localized variants
    """

    BUTTON_SELECTORS = [

        "div[role='button']",

        "span[role='button']",

        "div[tabindex='0']",

        "span"

    ]

    BUTTON_TEXT = [

        "See more",

        "More",

        "See More",

        "... More",

        "… More"

    ]

    def expand(self, container: Locator) -> bool:

        expanded = False

        # Try twice because Facebook often rerenders
        for _ in range(2):

            if self._expand_once(container):

                expanded = True

                time.sleep(0.6)

            else:

                break

        return expanded

    # -------------------------------------------------

    def _expand_once(self, container: Locator) -> bool:

        for selector in self.BUTTON_SELECTORS:

            buttons = container.locator(selector)

            count = buttons.count()

            for i in range(count):

                try:

                    button = buttons.nth(i)

                    text = button.inner_text(timeout=300).strip()

                    if not text:

                        continue

                    if not any(
                        keyword.lower() in text.lower()
                        for keyword in self.BUTTON_TEXT
                    ):
                        continue

                    if not button.is_visible():

                        continue

                    print("Expanding caption...")

                    button.scroll_into_view_if_needed()

                    try:

                        button.click(timeout=1000)

                    except Exception:

                        try:

                            button.evaluate(
                                "(el)=>el.click()"
                            )

                        except Exception:

                            continue

                    return True

                except Exception:

                    continue

        return False