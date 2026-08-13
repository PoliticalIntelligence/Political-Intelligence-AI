class AuthorParser:

    def extract(self, container):

        selectors = [

            "[data-ad-rendering-role='profile_name'] span",

            "h2 span",

            "h3 span",

            "strong span",

        ]

        for selector in selectors:

            try:

                locator = container.locator(selector).first

                text = locator.inner_text(timeout=500).strip()

                if text:
                    return text

            except:
                pass

        return ""