"""The BorrowBookOutputDTO carries plain data out of the use case."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class BorrowBookOutputDTO:
    success: bool
    book_item_id: str
    student_id: str
    due_date: date | None
    message: str
    book_title: str | None = None

