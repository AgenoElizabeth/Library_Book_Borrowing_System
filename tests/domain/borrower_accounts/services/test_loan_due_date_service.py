from datetime import date

from src.domain.borrower_accounts.services.LoanDueDateService import LoanDueDateService
from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType


def test_t6_the_due_date_depends_on_the_borrowing_date_and_the_loan_policy() -> None:
    # T6 - BR4: STUDENT loans last 14 days and STAFF loans last 28 days.
    # Arrange
    service = LoanDueDateService()
    borrowed_on = date(2026, 10, 1)

    # Act
    student_due_date = service.calculate_due_date(borrowed_on, BorrowerType.STUDENT)
    staff_due_date = service.calculate_due_date(borrowed_on, BorrowerType.STAFF)

    # Assert
    assert student_due_date == date(2026, 10, 15)
    assert staff_due_date == date(2026, 10, 29)
