from playwright.sync_api import Locator


class ContainerCollector:
    """
    Collect REAL Facebook post containers.

    Supports:
    - Public Facebook Pages
    - Public Facebook Profiles

    Ignores:
    - Comments
    - Loading skeletons
    - Duplicate containers
    """

    POST_LINK_SELECTORS = [

        "a[href*='/posts/']",
        "a[href*='/videos/']",
        "a[href*='/reel/']",
        "a[href*='/photo/?fbid=']",
        "a[href*='story_fbid=']",
        "a[href*='permalink']",

    ]

    COMMENT_LABELS = [
        "Comment by",
        "Reply by"
    ]

    def __init__(self, page):

        self.page = page

    # ------------------------------------------------------------

    def get_post_containers(self):

        posts = []
        seen = set()

        print("\nSearching for Facebook posts...\n")

        # Give Facebook time to finish rendering
        self.page.wait_for_timeout(3000)

        for selector in self.POST_LINK_SELECTORS:

            links = self.page.locator(selector)

            try:
                count = links.count()
            except Exception:
                continue

            print(f"{selector:<35} {count}")

            for i in range(count):

                try:

                    link = links.nth(i)

                    article = self.get_outermost_article(link)

                    if article is None:
                        continue

                    # Wait until attached
                    article.wait_for(
                        state="attached",
                        timeout=5000
                    )

                    # Skip loading skeletons
                    if self.is_loading(article):
                        continue

                    # Skip comments
                    if self.is_comment(article):
                        continue

                    # Must contain a real post link
                    if not self.has_post_link(article):
                        continue

                    # Must contain actual text
                    if not self.has_content(article):
                        continue

                    html = article.evaluate(
                        "el => el.outerHTML"
                    )

                    key = hash(html)

                    if key in seen:
                        continue

                    seen.add(key)

                    posts.append(article)

                except Exception:
                    continue

        print("\n" + "=" * 60)
        print(f"REAL POSTS FOUND : {len(posts)}")
        print("=" * 60)

        return posts

    # ------------------------------------------------------------

    def get_outermost_article(self, element: Locator):

        try:

            articles = element.locator(
                "xpath=ancestor::div[@role='article']"
            )

            total = articles.count()

            if total == 0:
                return None

            return articles.nth(total - 1)

        except Exception:
            return None

    # ------------------------------------------------------------

    def has_post_link(self, article: Locator):

        for selector in self.POST_LINK_SELECTORS:

            try:

                if article.locator(selector).count() > 0:
                    return True

            except Exception:
                pass

        return False

    # ------------------------------------------------------------

    def has_content(self, article: Locator):

        try:

            text = article.inner_text(timeout=1000)

            if len(text.strip()) > 30:
                return True

        except Exception:
            pass

        return False

    # ------------------------------------------------------------

    def is_loading(self, article: Locator):

        try:

            if article.locator(
                "[aria-label='Loading...']"
            ).count() > 0:

                print("Skipping loading skeleton")

                return True

        except Exception:
            pass

        return False

    # ------------------------------------------------------------

    def is_comment(self, article: Locator):

        try:

            label = article.get_attribute(
                "aria-label"
            )

            if label:

                for word in self.COMMENT_LABELS:

                    if word.lower() in label.lower():

                        print(
                            "Skipping Comment ->",
                            label
                        )

                        return True

        except Exception:
            pass

        return False