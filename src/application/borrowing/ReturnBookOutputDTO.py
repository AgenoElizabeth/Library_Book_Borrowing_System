"""The ReturnBookOutputDTO carries plain data out of the use case."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReturnBookOutputDTO:
    success: bool
    book_item_id: str
    student_id: str
    message: str
    book_title: str | None = None

