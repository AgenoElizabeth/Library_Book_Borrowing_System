"""The Borrow Book use case (main use case)."""

from collections.abc import Callable
from datetime import date

from src.application.borrowing.DomainEventHandler import DomainEventHandler
from src.application.borrowing.BorrowBookInputDTO import BorrowBookInputDTO
from src.application.borrowing.BorrowBookOutputDTO import BorrowBookOutputDTO
from src.domain.book_items.repositories.BookItemRepository import BookItemRepository
from src.domain.borrower_accounts.repositories.BorrowerAccountRepository import BorrowerAccountRepository
from src.domain.borrower_accounts.services.LoanDueDateService import LoanDueDateService


class BorrowBookApplicationService:
    """Coordinate the Borrow Book use case.

    The service holds no business rules. It loads aggregates, calls the domain,
    dispatches the Domain Event and saves the result. Every dependency is
    passed in from outside (Dependency Injection).
    """

    def __init__(
        self,
        book_items: BookItemRepository,
        borrower_accounts: BorrowerAccountRepository,
        due_date_service: LoanDueDateService,
        event_handler: DomainEventHandler,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._book_items = book_items
        self._borrower_accounts = borrower_accounts
        self._due_date_service = due_date_service
        self._event_handler = event_handler
        self._today = today

    def execute(self, request: BorrowBookInputDTO) -> BorrowBookOutputDTO:
        # BR6: the BookItem must exist before borrowing continues.
        book_item = self._book_items.find_by_id(request.book_item_id)
        if book_item is None:
            return self._failure(request, f"BookItem {request.book_item_id} does not exist.")

        account = self._borrower_accounts.find_by_id(request.student_id)
        if account is None:
            return self._failure(request, f"BorrowerAccount {request.student_id} does not exist.")

        try:
            borrowed_on = self._today()
            # BR4: the Domain Service calculates the due date.
            due_date = self._due_date_service.calculate_due_date(
                borrowed_on, account.borrower_type
            )
            # BR2: BookItem checks it is AVAILABLE and raises BookBorrowed.
            book_item.borrow(request.student_id, borrowed_on, due_date)
            # BR5: in-process event handling. BorrowerAccount checks BR3.
            for event in book_item.get_domain_events():
                self._event_handler.handle(event)
            book_item.clear_domain_events()
        except ValueError as error:
            # The BookItem is not saved, so it stays AVAILABLE in storage.
            return self._failure(request, str(error))

        self._book_items.save(book_item)
        return BorrowBookOutputDTO(
            success=True,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            due_date=due_date,
            message="Book borrowed successfully.",
            book_title=book_item.title,
        )

    @staticmethod
    def _failure(request: BorrowBookInputDTO, message: str) -> BorrowBookOutputDTO:
        return BorrowBookOutputDTO(
            success=False,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            due_date=None,
            message=message,
        )
