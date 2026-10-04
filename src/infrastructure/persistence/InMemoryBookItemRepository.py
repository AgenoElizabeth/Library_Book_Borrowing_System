"""An in-memory implementation of BookItemRepository."""

from copy import deepcopy

from src.domain.book_items.BookItem import BookItem
from src.domain.book_items.repositories.BookItemRepository import BookItemRepository


class InMemoryBookItemRepository(BookItemRepository):
    """Store BookItem aggregates in a dictionary.

    Copies are stored and returned, so unsaved changes never reach storage.
    """

    def __init__(self) -> None:
        self._book_items: dict[str, BookItem] = {}

    def find_by_id(self, book_item_id: str) -> BookItem | None:
        book_item = self._book_items.get(book_item_id)
        return deepcopy(book_item) if book_item is not None else None

    def save(self, book_item: BookItem) -> None:
        self._book_items[book_item.id] = deepcopy(book_item)
