import os
import time

from dotenv import load_dotenv

from ai_classifier.classifier import AIClassifier
from ai_classifier.knowledge_engine import KnowledgeEngine

from processors.sheet_writer import SheetWriter

# -----------------------------
# GIS
# -----------------------------
from gis.geocoder import GeoCoder


class AIProcessor:

    def __init__(self, logger):

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        self.logger = logger

        self.classifier = AIClassifier(api_key)

        self.knowledge = KnowledgeEngine()

        # -----------------------------
        # GIS
        # -----------------------------
        self.geocoder = GeoCoder()

        self.writer = SheetWriter(logger)

    # -----------------------------------------------------
    # PROCESS
    # -----------------------------------------------------

    def run(self, posts):

        self.logger.log("=" * 70)
        self.logger.log("AI PROCESSOR STARTED")
        self.logger.log("=" * 70)

        if not posts:

            self.logger.log("No posts received.")

            return

        success = 0
        failed = 0

        total = len(posts)

        for index, post in enumerate(posts, start=1):

            try:

                self.logger.log(
                    f"[{index}/{total}] Processing..."
                )

                caption = (post.text or "").strip()

                if not caption:

                    self.logger.log("Skipping empty caption.")

                    continue

                # ---------------------------------
                # AI Classification
                # ---------------------------------

                result = self.classifier.classify(caption)

                # ---------------------------------
                # Knowledge Enrichment
                # ---------------------------------

                result = self.knowledge.enrich(result)

                # ---------------------------------
                # GIS - Geocode Place of Visit
                # ---------------------------------

                geo = {
                    "latitude": "",
                    "longitude": "",
                    "status": "NOT_FOUND",
                    "source": ""
                }

                places = result.get("place_of_visit", [])

                if places:

                    try:

                        geo = self.geocoder.get_coordinates(
                            places[0]
                        )

                    except Exception as e:

                        self.logger.log(
                            f"Geocoding failed : {e}"
                        )

                # ---------------------------------
                # Standardized Author
                # ---------------------------------
                # Author must come from the Facebook Links master
                # via main.py -> post.author.
                # AI should never infer/rewrite the author from
                # the Facebook caption.

                if getattr(post, "author", None):
                    post.author = str(post.author).strip()

                # ---------------------------------
                # Write to Google Sheet
                # ---------------------------------

                self.writer.append_analysis(
                    post,
                    result,
                    geo
                )

                success += 1

                self.logger.log("Completed.")

                time.sleep(1)

            except Exception as e:

                failed += 1

                self.logger.log(f"Failed : {e}")

        self.logger.log("")
        self.logger.log("=" * 70)
        self.logger.log("AI PROCESSING COMPLETED")
        self.logger.log("=" * 70)

        self.logger.log(f"Processed : {total}")
        self.logger.log(f"Success   : {success}")
        self.logger.log(f"Failed    : {failed}")