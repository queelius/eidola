"""longshade: Conversable persona generation from personal data."""

__version__ = "0.1.0"

from .models import (
    Message,
    Conversation,
    Chunk,
    Writing,
    Email,
    Bookmark,
    Photo,
    Reading,
)

__all__ = [
    "__version__",
    "Message",
    "Conversation",
    "Chunk",
    "Writing",
    "Email",
    "Bookmark",
    "Photo",
    "Reading",
]
