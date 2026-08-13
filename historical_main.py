import sys

from browser.browser_manager import BrowserManager
from collectors.facebook.historical_collector import HistoricalFacebookCollector

from exporters.json_exporter import JsonExporter
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter
from exporters.google_sheets_exporter import GoogleSheetsExporter

from utils.logger import Logger


# ----------------------------------------------------------
# UTF-8 Console
# ----------------------------------------------------------

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ----------------------------------------------------------
# Global Logger
# ----------------------------------------------------------

logger = Logger()


# ----------------------------------------------------------
# Historical Scraper Settings
# ----------------------------------------------------------

HISTORY_DAYS = 45

FACEBOOK_PAGE = "https://www.facebook.com/SanatanPandeyBallia/posts"


# ----------------------------------------------------------
# Export Helpers
# ----------------------------------------------------------

def export_all(posts):

    exporters = [

        ("JSON", JsonExporter()),

        ("CSV", CSVExporter()),

        ("Excel", ExcelExporter()),

        ("Google Sheets", GoogleSheetsExporter(logger))

    ]

    for name, exporter in exporters:

        try:

            logger.log(f"Exporting to {name}...")

            exporter.export(posts)

            logger.log(f"{name} export completed.")

        except PermissionError:

            logger.log(f"{name} export skipped (file is open).")

        except Exception as e:

            logger.log(f"{name} export failed.")

            logger.log(str(e))

    logger.log("All exports completed.")


# ----------------------------------------------------------
# Display Posts
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():

    logger.log("=" * 70)
    logger.log("FACEBOOK HISTORICAL SCRAPER")
    logger.log("=" * 70)

    browser = None
    facebook = None

    try:

        logger.log("Initializing Browser...")

        browser = BrowserManager(logger)

        browser.start()

        facebook = HistoricalFacebookCollector(

            browser_manager=browser,

            history_days=HISTORY_DAYS

        )

        logger.log(f"Opening Facebook Page: {FACEBOOK_PAGE}")

        facebook.open_page(FACEBOOK_PAGE)

        logger.log(
            f"Collecting last {HISTORY_DAYS} days of posts..."
        )

        posts = facebook.get_posts()

        logger.log(f"Collected {len(posts)} posts.")

        if not posts:

            logger.log("No posts collected.")

            return

        export_all(posts)

        display_posts(posts)

        logger.log("Historical scraping completed successfully.")

    except KeyboardInterrupt:

        logger.log("Scraper stopped by user.")

    except Exception as e:

        logger.log("APPLICATION ERROR")

        logger.log(type(e).__name__)

        logger.log(str(e))

    finally:

        logger.log("Closing application...")

        if facebook:

            try:

                facebook.close()

            except Exception as e:

                logger.log(
                    f"Error closing collector: {e}"
                )

        if browser:

            try:

                browser.close()

            except Exception as e:

                logger.log(
                    f"Error closing browser: {e}"
                )

        logger.log("Application Finished.")


# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------

if __name__ == "__main__":

    main()