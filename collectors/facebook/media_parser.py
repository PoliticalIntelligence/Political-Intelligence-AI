from typing import Dict

from playwright.sync_api import Locator


class MediaParser:
    """
    Extracts media belonging ONLY to the Facebook post.

    Returns
    -------
    media_type
    has_image
    is_video
    is_reel
    images
    videos
    """

    IMAGE_SELECTORS = [

        "a[href*='/photo/'] img",

        "a[href*='photo/?fbid='] img",

        "img[data-imgperflogname]",

        "img[referrerpolicy]"

    ]

    VIDEO_SELECTORS = [

        "video",

        "video source"

    ]

    REEL_SELECTOR = "a[href*='/reel/']"

    def extract(self, container: Locator) -> Dict:

        media = {

            "media_type": "text",

            "has_image": False,

            "is_video": False,

            "is_reel": False,

            "images": [],

            "videos": []

        }

        media["images"] = self.extract_images(container)

        media["videos"] = self.extract_videos(container)

        media["has_image"] = len(media["images"]) > 0

        media["is_video"] = len(media["videos"]) > 0

        media["is_reel"] = (
            container.locator(self.REEL_SELECTOR).count() > 0
        )

        if media["is_reel"]:

            media["media_type"] = "reel"

        elif media["is_video"]:

            media["media_type"] = "video"

        elif media["has_image"]:

            media["media_type"] = "image"

        return media

    # -------------------------------------------------

    def extract_images(self, container: Locator):

        images = []

        seen = set()

        for selector in self.IMAGE_SELECTORS:

            try:

                locators = container.locator(selector)

                total = locators.count()

                for i in range(total):

                    src = locators.nth(i).get_attribute("src")

                    if not src:

                        continue

                    if "emoji" in src.lower():

                        continue

                    if "profile" in src.lower():

                        continue

                    if "scontent" not in src:

                        continue

                    if src in seen:

                        continue

                    seen.add(src)

                    images.append(src)

            except Exception:

                continue

        return images

    # -------------------------------------------------

    def extract_videos(self, container: Locator):

        videos = []

        seen = set()

        for selector in self.VIDEO_SELECTORS:

            try:

                locators = container.locator(selector)

                total = locators.count()

                for i in range(total):

                    src = locators.nth(i).get_attribute("src")

                    if not src:

                        continue

                    if src in seen:

                        continue

                    seen.add(src)

                    videos.append(src)

            except Exception:

                continue

        return videos