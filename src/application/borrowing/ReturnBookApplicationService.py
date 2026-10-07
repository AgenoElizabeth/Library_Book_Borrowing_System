from collections.abc import Callable
from datetime import date

from src.application.borrowing.ReturnBookInputDTO import ReturnBookInputDTO
from src.application.borrowing.ReturnBookOutputDTO import ReturnBookOutputDTO
from src.domain.book_items.repositories.BookItemRepository import BookItemRepository
from src.domain.borrower_accounts.repositories.BorrowerAccountRepository import BorrowerAccountRepository


class ReturnBookApplicationService:
    """Coordinate the Return Book use case."""

    def __init__(
        self,
        book_items: BookItemRepository,
        borrower_accounts: BorrowerAccountRepository,
        today: Callable[[], date] | None = None,
    ) -> None:
        self._book_items = book_items
        self._borrower_accounts = borrower_accounts
        self._today = today or date.today

    def execute(self, request: ReturnBookInputDTO) -> ReturnBookOutputDTO:
        book_item = self._book_items.find_by_id(request.book_item_id)
        if book_item is None:
            return self._failure(request, f"BookItem {request.book_item_id} does not exist.")

        account = self._borrower_accounts.find_by_id(request.student_id)
        if account is None:
            return self._failure(request, f"BorrowerAccount {request.student_id} does not exist.")

        # Find active borrowing to inspect due date before closing
        borrowing = next(
            (b for b in account.active_borrowings if b.book_item_id == request.book_item_id),
            None,
        )
        if borrowing is None:
            return self._failure(request, f"Borrower {request.student_id} has no active borrowing for {request.book_item_id}.")

        due_date = borrowing.due_date
        return_date = self._today()
        days_overdue = 0
        fine_amount = 0.0

        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            rate = 0.50 if account.borrower_type.name == "STAFF" else 1.00
            fine_amount = round(days_overdue * rate, 2)

        try:
            account.close_borrowing(request.book_item_id)
            book_item.return_to_library()
        except ValueError as error:
            return self._failure(request, str(error))

        self._borrower_accounts.save(account)
        self._book_items.save(book_item)

        msg = f"Book returned successfully. ({days_overdue} days overdue - Fine: ${fine_amount:.2f})" if days_overdue > 0 else "Book returned on time successfully."

        return ReturnBookOutputDTO(
            success=True,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            message=msg,
            book_title=book_item.title,
            due_date=due_date,
            return_date=return_date,
            days_overdue=days_overdue,
            fine_amount=fine_amount,
        )

    @staticmethod
    def _failure(request: ReturnBookInputDTO, message: str) -> ReturnBookOutputDTO:
        return ReturnBookOutputDTO(
            success=False,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            message=message,
        )
