"""The states a physical book copy can be in."""

from enum import Enum


class BookItemStatus(Enum):
    """Restrict a BookItem to the two states the domain knows about."""

    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
