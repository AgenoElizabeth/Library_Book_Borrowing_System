"""The Borrowing child entity in the BorrowerAccount aggregate."""

from datetime import date
from uuid import uuid4

from src.domain.shared.Entity import Entity


class Borrowing(Entity):
    """One active borrowing of a BookItem by a borrower.

    Borrowing is a child entity, not a third aggregate root. Only
    BorrowerAccount creates it, so the borrowing limit (BR3) is always checked.
    """

    def __init__(self, book_item_id: str, borrowed_on: date, due_date: date) -> None:
        super().__init__(uuid4().hex)
        self._book_item_id = book_item_id
        self._borrowed_on = borrowed_on
        self._due_date = due_date

    @property
    def book_item_id(self) -> str:
        return self._book_item_id

    @property
    def borrowed_on(self) -> date:
        return self._borrowed_on

    @property
    def due_date(self) -> date:
        return self._due_date
