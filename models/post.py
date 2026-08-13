from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Post:
    """
    Represents a single Facebook post.

    This model is shared across all parsers and exporters.
    """

    # ---------------------------------------------------------
    # Basic Information
    # ---------------------------------------------------------

    url: str = ""
    text: str = ""
    timestamp: str = ""
    author: str = ""

    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Engagement Summary
    # ---------------------------------------------------------

    reactions: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0

    # ---------------------------------------------------------
    # Reaction Breakdown
    # ---------------------------------------------------------

    like: Optional[int] = 0
    love: Optional[int] = 0
    care: Optional[int] = 0
    haha: Optional[int] = 0
    wow: Optional[int] = 0
    sad: Optional[int] = 0
    angry: Optional[int] = 0

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    scraped_at: str = ""
    source_page: str = ""