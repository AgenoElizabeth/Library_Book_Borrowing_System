"""The BorrowBookInputDTO carries plain data into the use case."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BorrowBookInputDTO:
    student_id: str
    book_item_id: str
