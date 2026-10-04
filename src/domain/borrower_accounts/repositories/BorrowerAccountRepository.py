"""The BorrowerAccountRepository contract."""

from abc import ABC, abstractmethod

from src.domain.borrower_accounts.BorrowerAccount import BorrowerAccount


class BorrowerAccountRepository(ABC):
    """Retrieve and store BorrowerAccount aggregates without exposing storage details.

    ``find_by_id`` returns a separate copy of the aggregate. Changes reach
    storage only when the aggregate is passed to ``save``.
    """

    @abstractmethod
    def find_by_id(self, student_id: str) -> BorrowerAccount | None:
        """Return the BorrowerAccount, or ``None`` when it does not exist."""

    @abstractmethod
    def save(self, account: BorrowerAccount) -> None:
        """Store the current state of the BorrowerAccount."""
