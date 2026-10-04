"""The ReturnBookInputDTO carries plain data into the use case."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReturnBookInputDTO:
    student_id: str
    book_item_id: str
