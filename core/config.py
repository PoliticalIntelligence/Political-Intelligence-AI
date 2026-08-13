from pathlib import Path


class Config:
    """
    Global configuration for the Political Intelligence AI project.
    """

    # --------------------------------------------------
    # Project Directories
    # --------------------------------------------------
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    DATA_DIR = PROJECT_ROOT / "data"
    LOG_DIR = PROJECT_ROOT / "logs"
    REPORT_DIR = PROJECT_ROOT / "reports"

    SCREENSHOT_DIR = LOG_DIR / "screenshots"
    HTML_DIR = LOG_DIR / "html"

    # --------------------------------------------------
    # Browser Configuration
    # --------------------------------------------------
    HEADLESS = False

    SLOW_MO = 500

    VIEWPORT = {
        "width": 1400,
        "height": 900
    }

    DEFAULT_TIMEOUT = 60000

    # --------------------------------------------------
    # Create required directories automatically
    # --------------------------------------------------
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)