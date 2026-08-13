from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FacebookPost:
    """
    Represents one Facebook post.
    """

    leader_name: str

    page_name: str

    post_text: str = ""

    post_url: str = ""

    published_at: str = ""

    scraped_at: datetime = field(default_factory=datetime.utcnow)

    likes: int = 0

    comments: int = 0

    shares: int = 0

    images: list[str] = field(default_factory=list)

    videos: list[str] = field(default_factory=list)

    is_video: bool = False

    is_reel: bool = False

    is_live: bool = False