"""The Return Book use case."""

from src.application.borrowing.ReturnBookInputDTO import ReturnBookInputDTO
from src.application.borrowing.ReturnBookOutputDTO import ReturnBookOutputDTO
from src.domain.book_items.repositories.BookItemRepository import BookItemRepository
from src.domain.borrower_accounts.repositories.BorrowerAccountRepository import BorrowerAccountRepository


class ReturnBookApplicationService:
    """Coordinate the Return Book use case.

    Return Book completes the borrowing that BookBorrowed recorded. It raises no
    Domain Event because the system has exactly one.
    """

    def __init__(
        self,
        book_items: BookItemRepository,
        borrower_accounts: BorrowerAccountRepository,
    ) -> None:
        self._book_items = book_items
        self._borrower_accounts = borrower_accounts

    def execute(self, request: ReturnBookInputDTO) -> ReturnBookOutputDTO:
        book_item = self._book_items.find_by_id(request.book_item_id)
        if book_item is None:
            return self._failure(request, f"BookItem {request.book_item_id} does not exist.")

        account = self._borrower_accounts.find_by_id(request.student_id)
        if account is None:
            return self._failure(request, f"BorrowerAccount {request.student_id} does not exist.")

        try:
            account.close_borrowing(request.book_item_id)
            book_item.return_to_library()
        except ValueError as error:
            return self._failure(request, str(error))

        self._borrower_accounts.save(account)
        self._book_items.save(book_item)
        return ReturnBookOutputDTO(
            success=True,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            message="Book returned successfully.",
            book_title=book_item.title,
        )

    @staticmethod
    def _failure(request: ReturnBookInputDTO, message: str) -> ReturnBookOutputDTO:
        return ReturnBookOutputDTO(
            success=False,
            book_item_id=request.book_item_id,
            student_id=request.student_id,
            message=message,
        )
