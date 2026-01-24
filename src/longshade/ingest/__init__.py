"""Input ingesters for various data sources."""

from .base import Ingester
from .conversations import ConversationIngester
from .writings import WritingIngester
from .emails import EmailIngester
from .bookmarks import BookmarkIngester
from .photos import PhotoIngester
from .reading import ReadingIngester
from .voice import VoiceIngester

__all__ = [
    "Ingester",
    "ConversationIngester",
    "WritingIngester",
    "EmailIngester",
    "BookmarkIngester",
    "PhotoIngester",
    "ReadingIngester",
    "VoiceIngester",
]
