"""An in-memory implementation of BorrowerAccountRepository."""

from copy import deepcopy

from src.domain.borrower_accounts.BorrowerAccount import BorrowerAccount
from src.domain.borrower_accounts.repositories.BorrowerAccountRepository import BorrowerAccountRepository


class InMemoryBorrowerAccountRepository(BorrowerAccountRepository):
    """Store BorrowerAccount aggregates in a dictionary.

    Copies are stored and returned, so unsaved changes never reach storage.
    """

    def __init__(self) -> None:
        self._accounts: dict[str, BorrowerAccount] = {}

    def find_by_id(self, student_id: str) -> BorrowerAccount | None:
        account = self._accounts.get(student_id)
        return deepcopy(account) if account is not None else None

    def save(self, account: BorrowerAccount) -> None:
        self._accounts[account.id] = deepcopy(account)
