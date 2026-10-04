"""The BookBorrowed domain event (BR5 - Follow-up Rule)."""

from dataclasses import dataclass
from datetime import date

from src.domain.shared.DomainEvent import DomainEvent


@dataclass(frozen=True, slots=True)
class BookBorrowed(DomainEvent):
    """A BookItem has changed from AVAILABLE to BORROWED.

    This is the only Domain Event in the system. It asks the BorrowerAccount
    aggregate to record the new active borrowing.
    """

    book_item_id: str
    student_id: str
    borrowed_on: date
    due_date: date
