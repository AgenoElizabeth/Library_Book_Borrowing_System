from datetime import date

import pytest

from src.domain.borrower_accounts.BorrowerAccount import BorrowerAccount
from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType


def test_t5_a_borrower_at_the_borrowing_limit_cannot_borrow_again() -> None:
    # T5 - BR3 (boundary): limit 5 with 5 active borrowings rejects a sixth.
    # Arrange
    account = BorrowerAccount("ST123", BorrowerType.STUDENT, borrowing_limit=5)
    for number in range(1, 6):
        account.record_borrowing(f"BI00{number}", date(2026, 10, 1), date(2026, 10, 15))

    # Act
    with pytest.raises(ValueError) as exception_info:
        account.record_borrowing("BI006", date(2026, 10, 1), date(2026, 10, 15))

    # Assert
    assert "has reached the borrowing limit of 5" in str(exception_info.value)
    assert len(account.active_borrowings) == 5
