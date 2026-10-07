"""The BorrowerAccount aggregate root (Aggregate B).

BorrowerAccount protects the rule that a borrower never has more active
borrowings than the borrowing limit (BR3). Borrowing entities are created and
removed only through this root.
"""

from datetime import date

from src.domain.borrower_accounts.borrowings.Borrowing import Borrowing
from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType
from src.domain.shared.AggregateRoot import AggregateRoot


class BorrowerAccount(AggregateRoot):
    """A borrower's active borrowings, identified by the student id."""

    def __init__(
        self,
        student_id: str,
        borrower_type: BorrowerType,
        borrowing_limit: int,
    ) -> None:
        super().__init__(student_id)
        if borrowing_limit <= 0:
            raise ValueError("A borrowing limit must be greater than zero.")

        self._borrower_type = borrower_type
        self._borrowing_limit = borrowing_limit
        self._active_borrowings: list[Borrowing] = []

    @property
    def id(self) -> str:
        """Return the string student/staff identity of this BorrowerAccount."""
        return str(self._id)

    @property
    def borrower_type(self) -> BorrowerType:
        return self._borrower_type

    @property
    def borrowing_limit(self) -> int:
        return self._borrowing_limit

    @property
    def active_borrowings(self) -> tuple[Borrowing, ...]:
        """Return the active borrowings as a read-only tuple."""

        return tuple(self._active_borrowings)

    def record_borrowing(
        self,
        book_item_id: str,
        borrowed_on: date,
        due_date: date,
    ) -> Borrowing:
        """Protect BR3 before creating a new Borrowing.

        The check happens before the change, so a rejected borrowing leaves
        the account unchanged.
        """

        if len(self._active_borrowings) >= self._borrowing_limit:
            raise ValueError(
                f"Borrower {self.id} has reached the borrowing limit "
                f"of {self._borrowing_limit}."
            )

        borrowing = Borrowing(book_item_id, borrowed_on, due_date)
        self._active_borrowings.append(borrowing)
        return borrowing

    def close_borrowing(self, book_item_id: str) -> Borrowing:
        """Remove the active Borrowing for a returned BookItem."""

        borrowing = next(
            (
                candidate
                for candidate in self._active_borrowings
                if candidate.book_item_id == book_item_id
            ),
            None,
        )
        if borrowing is None:
            raise ValueError(
                f"Borrower {self.id} has no active borrowing for {book_item_id}."
            )

        self._active_borrowings.remove(borrowing)
        return borrowing
