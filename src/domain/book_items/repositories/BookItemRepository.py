"""The BookItemRepository contract."""

from abc import ABC, abstractmethod

from src.domain.book_items.BookItem import BookItem


class BookItemRepository(ABC):
    """Retrieve and store BookItem aggregates without exposing storage details.

    ``find_by_id`` returns a separate copy of the aggregate. Changes reach
    storage only when the aggregate is passed to ``save``.
    """

    @abstractmethod
    def find_by_id(self, book_item_id: str) -> BookItem | None:
        """Return the BookItem, or ``None`` when it does not exist (BR6)."""

    @abstractmethod
    def save(self, book_item: BookItem) -> None:
        """Store the current state of the BookItem."""
