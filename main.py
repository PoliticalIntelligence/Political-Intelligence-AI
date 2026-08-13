import sys
from datetime import datetime

from browser.browser_manager import BrowserManager
from collectors.facebook.collector import FacebookCollector
from exporters.json_exporter import JsonExporter
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter
from exporters.google_sheets_exporter import GoogleSheetsExporter
from processors.ai_processor import AIProcessor
from utils.logger import Logger
from utils.facebook_sheet_reader import FacebookSheetReader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = Logger()


def export_all(posts, run_date=None):
    exporters = [
        ("JSON", JsonExporter()),
        ("CSV", CSVExporter()),
        ("Excel", ExcelExporter()),
        ("Google Sheets", GoogleSheetsExporter(logger)),
    ]

    for name, exporter in exporters:
        try:
            logger.log(f"Exporting to {name}...")
            if name == "Google Sheets":
                exporter.export(posts, run_date=run_date)
            else:
                exporter.export(posts)
            logger.log(f"{name} export completed.")
        except PermissionError:
            logger.log(f"{name} export skipped (file is open).")
        except Exception as exc:
            logger.log(f"{name} export failed.")
            logger.log(f"{type(exc).__name__}: {exc}")

    logger.log("All exports completed.")


def display_posts(posts):
    logger.log(f"Displaying {len(posts)} posts.")
    for index, post in enumerate(posts, start=1):
        print("\n" + "=" * 80)
        print(f"POST #{index}")
        print("=" * 80)
        print(f"Author      : {post.author}")
        print(f"Timestamp   : {post.timestamp}")
        print(f"URL         : {post.url}")
        print(f"Source Page : {post.source_page}")
        print(f"Scraped At  : {post.scraped_at}")
        print()
        print(post.text or "[No text]")
        print()
        print(f"Reactions : {post.reactions}")
        print(f"Comments  : {post.comments}")
        print(f"Shares    : {post.shares}")
        print(f"Images    : {len(post.images)}")
        print(f"Videos    : {len(post.videos)}")


def main(run_date=None):
    if run_date is None:
        run_date = (
            sys.argv[1]
            if len(sys.argv) > 1
            else datetime.now().strftime("%Y-%m-%d")
        )

    try:
        datetime.strptime(run_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Invalid run date: {run_date}. Use YYYY-MM-DD format."
        ) from exc

    logger.log("=" * 70)
    logger.log("POLITICAL INTELLIGENCE AI")
    logger.log(f"RUN DATE : {run_date}")
    logger.log("=" * 70)

    browser = None
    facebook = None

    try:
        logger.log("Initializing browser manager...")
        browser = BrowserManager(logger)
        browser.start()
        facebook = FacebookCollector(browser)

        reader = FacebookSheetReader()
        pages = reader.get_pages()

        if not pages:
            logger.log("No active Facebook pages found.")
            return

        logger.log(f"{len(pages)} Facebook pages loaded.")
        logger.log("Author standardization source: Facebook Links master.")

        all_posts = []

        for index, page in enumerate(pages, start=1):
            logger.log("")
            logger.log("=" * 80)
            logger.log(f"[{index}/{len(pages)}] {page['name']}")
            logger.log("=" * 80)

            try:
                logger.log(f"Opening {page['name']} ({page['url']})")
                facebook.open_page(page["url"])

                logger.log("Collecting posts...")
                posts = facebook.get_posts() or []
                logger.log(f"Collected {len(posts)} posts.")

                if not posts:
                    logger.log("No posts found.")
                    continue

                # Facebook Links master is the single source of truth
                # for the standardized Author value.
                for post in posts:
                    post.author = str(page["name"] or "").strip()
                    post.page_name = page["name"]
                    post.page_id = page["id"]
                    post.page_url = page["url"]

                all_posts.extend(posts)
                logger.log(f"Completed : {page['name']}")

            except Exception as exc:
                logger.log(f"Failed to scrape {page['name']}")
                logger.log(f"{type(exc).__name__}: {exc}")

            finally:
                try:
                    facebook.close()
                except Exception as exc:
                    logger.log(
                        f"Error closing Facebook context: "
                        f"{type(exc).__name__}: {exc}"
                    )

        logger.log("")
        logger.log("=" * 70)
        logger.log("ALL FACEBOOK PAGES SCRAPED")
        logger.log("=" * 70)
        logger.log(f"Total Posts Collected : {len(all_posts)}")

        logger.log("")
        logger.log("=" * 70)
        logger.log("EXPORTING ALL POSTS")
        logger.log("=" * 70)

        export_all(all_posts, run_date=run_date)

        logger.log("")
        logger.log("=" * 70)
        logger.log("STARTING AI PROCESSING")
        logger.log("=" * 70)

        try:
            processor = AIProcessor(logger)
            processor.run(all_posts)

            logger.log("")
            logger.log("=" * 70)
            logger.log("AI PROCESSING FINISHED")
            logger.log("=" * 70)

        except Exception as exc:
            logger.log("")
            logger.log("=" * 70)
            logger.log("AI PROCESSING FAILED")
            logger.log("=" * 70)
            logger.log(f"{type(exc).__name__}: {exc}")

        display_posts(all_posts)

    except KeyboardInterrupt:
        logger.log("Scraper stopped by user.")

    except Exception as exc:
        logger.log("APPLICATION ERROR")
        logger.log(f"{type(exc).__name__}: {exc}")

    finally:
        logger.log("Shutting down application...")

        if facebook:
            try:
                facebook.close()
            except Exception:
                pass

        if browser:
            try:
                browser.close()
            except Exception as exc:
                logger.log(
                    f"Error closing browser manager: "
                    f"{type(exc).__name__}: {exc}"
                )

        logger.log("Application finished.")


if __name__ == "__main__":
    main()
