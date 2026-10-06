"""The BookItem aggregate root (Aggregate A).

An aggregate is a group of domain objects that must remain consistent together.
BookItem controls the state of one physical book copy and raises the BookBorrowed
event when it is borrowed.
"""

from datetime import date

from src.domain.book_items.events.BookBorrowed import BookBorrowed
from src.domain.book_items.value_objects.BookItemStatus import BookItemStatus
from src.domain.book_items.value_objects.ISBN import ISBN
from src.domain.shared.AggregateRoot import AggregateRoot


class BookItem(AggregateRoot):
    """One physical copy of a book, identified by its book item id.

    Different copies can share an ISBN but have different states, which is why
    each copy needs its own identity (BR2).
    """

    def __init__(
        self,
        book_item_id: str,
        isbn: ISBN,
        title: str = "Untitled Computer Science Book",
        status: BookItemStatus = BookItemStatus.AVAILABLE,
    ) -> None:
        super().__init__(book_item_id)
        self._isbn = isbn
        self._title = title
        self._status = status

    @property
    def isbn(self) -> ISBN:
        """Return the ISBN shared by every copy of this book."""

        return self._isbn

    @property
    def title(self) -> str:
        """Return the title of this book."""

        return self._title

    @property
    def status(self) -> BookItemStatus:
        """Return whether this copy is AVAILABLE or BORROWED."""

        return self._status

    def borrow(self, student_id: str, borrowed_on: date, due_date: date) -> None:
        """Protect BR2: only an AVAILABLE copy can be borrowed.

        After the state changes, BookItem raises BookBorrowed so that the
        BorrowerAccount aggregate can record the borrowing (BR5).
        """

        if self._status is not BookItemStatus.AVAILABLE:
            raise ValueError(f"BookItem {self.id} is already borrowed.")

        self._status = BookItemStatus.BORROWED
        self._raise_domain_event(
            BookBorrowed(self.id, student_id, borrowed_on, due_date)
        )

    def return_to_library(self) -> None:
        """Make a BORROWED copy AVAILABLE again (Return Book use case)."""

        if self._status is not BookItemStatus.BORROWED:
            raise ValueError(f"BookItem {self.id} is not borrowed.")

        self._status = BookItemStatus.AVAILABLE
