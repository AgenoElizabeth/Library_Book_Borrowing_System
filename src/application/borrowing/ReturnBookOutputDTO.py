from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ReturnBookOutputDTO:
    success: bool
    book_item_id: str
    student_id: str
    message: str
    book_title: str | None = None
    due_date: date | None = None
    return_date: date | None = None
    days_overdue: int = 0
    fine_amount: float = 0.0

