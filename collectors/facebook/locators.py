"""
Central place for all Facebook selectors.

Whenever Facebook changes its HTML,
we only update this file.
"""


class FacebookLocators:

    # ----------------------------
    # Post Containers
    # ----------------------------
    POST_CONTAINER = 'div[role="article"]'

    # ----------------------------
    # Post Text
    # ----------------------------
    POST_TEXT = 'div[data-ad-preview="message"]'

    # Fallback text selector
    FALLBACK_TEXT = 'div[dir="auto"]'

    # ----------------------------
    # Login Popup
    # ----------------------------
    LOGIN_DIALOG = '[role="dialog"]'

    CLOSE_BUTTON = '[aria-label="Close"]'

    # ----------------------------
    # Future Selectors
    # ----------------------------
    POST_DATE = ""

    IMAGE = ""

    VIDEO = ""

    LIKE_COUNT = ""

    COMMENT_COUNT = ""

    SHARE_COUNT = ""