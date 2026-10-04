"""The LoanDueDateService domain service (BR4 - Cross-Concept Rule)."""

from collections.abc import Mapping
from datetime import date, timedelta

from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType


class LoanDueDateService:
    """Calculate a due date from the borrowing date and the loan policy.

    The calculation needs information from more than one concept, so it does
    not belong to BookItem or BorrowerAccount.
    """

    # The default loan policy: number of loan days for each borrower type.
    DEFAULT_LOAN_DAYS: Mapping[BorrowerType, int] = {
        BorrowerType.STUDENT: 14,
        BorrowerType.STAFF: 28,
    }

    def __init__(self, loan_days: Mapping[BorrowerType, int] | None = None) -> None:
        """Use the default loan policy unless a different policy is supplied."""

        self._loan_days = dict(loan_days or self.DEFAULT_LOAN_DAYS)

    def calculate_due_date(self, borrowed_on: date, borrower_type: BorrowerType) -> date:
        """Return the due date, or raise when no loan policy applies."""

        if borrower_type not in self._loan_days:
            raise ValueError(f"There is no loan policy for {borrower_type.value}.")

        return borrowed_on + timedelta(days=self._loan_days[borrower_type])
