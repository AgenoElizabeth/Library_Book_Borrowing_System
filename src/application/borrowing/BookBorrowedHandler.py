from src.domain.book_items.events.BookBorrowed import BookBorrowed
from src.domain.borrower_accounts.repositories.BorrowerAccountRepository import BorrowerAccountRepository
from src.domain.shared.DomainEvent import DomainEvent


class BookBorrowedHandler:
    """Ask Aggregate B (BorrowerAccount) to record the new active borrowing.

    BorrowerAccount checks BR3 before it accepts the borrowing. When the limit
    would be exceeded it raises ``ValueError`` and nothing is saved.
    """

    def __init__(self, borrower_accounts: BorrowerAccountRepository) -> None:
        self._borrower_accounts = borrower_accounts

    def handle(self, event: DomainEvent) -> None:
        if not isinstance(event, BookBorrowed):
            return

        account = self._borrower_accounts.find_by_id(event.student_id)
        if account is None:
            raise ValueError(f"BorrowerAccount {event.student_id} does not exist.")

        account.record_borrowing(event.book_item_id, event.borrowed_on, event.due_date)
        self._borrower_accounts.save(account)
