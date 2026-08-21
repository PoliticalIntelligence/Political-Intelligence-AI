import os

from dotenv import load_dotenv

from ai_classifier.classifier import AIClassifier
from ai_classifier.knowledge_engine import KnowledgeEngine
from processors.sheet_writer import SheetWriter


class AIProcessor:
    """
    AI classification + knowledge enrichment + Google Sheets writing.

    Gemini requests are rate-limited inside AIClassifier to stay
    safely below the free-tier requests-per-minute limit.

    GIS/geocoding has been removed. The existing SheetWriter in the
    current project still expects a `geo` argument, so we provide a
    blank geo object for compatibility.
    """

    def __init__(self, logger):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        self.logger = logger

        self.classifier = AIClassifier(api_key)

        self.knowledge = KnowledgeEngine()

        self.writer = SheetWriter(logger)

    def run(self, posts):

        self.logger.log("=" * 70)
        self.logger.log("AI PROCESSOR STARTED")
        self.logger.log("=" * 70)

        if not posts:
            self.logger.log("No posts received.")
            return

        success = 0
        failed = 0
        skipped = 0

        total = len(posts)

        self.logger.log(
            f"Total posts received: {total}"
        )

        self.logger.log(
            "Gemini rate limit protection: "
            "approximately 10 requests/minute"
        )

        for index, post in enumerate(posts, start=1):

            try:

                self.logger.log(
                    f"[{index}/{total}] Processing..."
                )

                caption = (post.text or "").strip()

                # -------------------------------------------------
                # EMPTY CAPTION
                # -------------------------------------------------

                if not caption:

                    skipped += 1

                    self.logger.log(
                        f"[{index}/{total}] "
                        "Skipped - empty caption."
                    )

                    continue

                # -------------------------------------------------
                # AI CLASSIFICATION
                # -------------------------------------------------

                self.logger.log(
                    f"[{index}/{total}] "
                    "Sending to Gemini..."
                )

                result = self.classifier.classify(
                    caption
                )

                # -------------------------------------------------
                # KNOWLEDGE ENRICHMENT
                # -------------------------------------------------

                result = self.knowledge.enrich(
                    result
                )

                # -------------------------------------------------
                # STANDARDIZED AUTHOR
                # -------------------------------------------------

                if getattr(post, "author", None):

                    post.author = str(
                        post.author
                    ).strip()

                # -------------------------------------------------
                # GIS COMPATIBILITY OBJECT
                # -------------------------------------------------

                geo = {
                    "latitude": "",
                    "longitude": "",
                    "status": "NOT_FOUND",
                    "source": "",
                }

                # -------------------------------------------------
                # WRITE TO GOOGLE SHEET
                # -------------------------------------------------

                self.writer.append_analysis(
                    post,
                    result,
                    geo,
                )

                success += 1

                self.logger.log(
                    f"[{index}/{total}] Completed."
                )

            except Exception as exc:

                failed += 1

                self.logger.log(
                    f"[{index}/{total}] "
                    f"Failed: "
                    f"{type(exc).__name__}: {exc}"
                )

        # ---------------------------------------------------------
        # FINAL SUMMARY
        # ---------------------------------------------------------

        self.logger.log("")

        self.logger.log("=" * 70)
        self.logger.log("AI PROCESSING COMPLETED")
        self.logger.log("=" * 70)

        self.logger.log(
            f"Total received : {total}"
        )

        self.logger.log(
            f"Success        : {success}"
        )

        self.logger.log(
            f"Skipped        : {skipped}"
        )

        self.logger.log(
            f"Failed         : {failed}"
        )

        self.logger.log("=" * 70)