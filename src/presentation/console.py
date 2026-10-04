"""A minimal console interface. It wires dependencies and calls the use cases."""

from src.application.borrowing.BookBorrowedHandler import BookBorrowedHandler
from src.application.borrowing.BorrowBookApplicationService import BorrowBookApplicationService
from src.application.borrowing.BorrowBookInputDTO import BorrowBookInputDTO
from src.application.borrowing.ReturnBookApplicationService import ReturnBookApplicationService
from src.application.borrowing.ReturnBookInputDTO import ReturnBookInputDTO
from src.domain.book_items.BookItem import BookItem
from src.domain.book_items.value_objects.ISBN import ISBN
from src.domain.borrower_accounts.BorrowerAccount import BorrowerAccount
from src.domain.borrower_accounts.services.LoanDueDateService import LoanDueDateService
from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType
from src.infrastructure.persistence.InMemoryBookItemRepository import InMemoryBookItemRepository
from src.infrastructure.persistence.InMemoryBorrowerAccountRepository import InMemoryBorrowerAccountRepository


def main() -> None:
    book_items = InMemoryBookItemRepository()
    borrower_accounts = InMemoryBorrowerAccountRepository()
    book_items.save(BookItem("BI001", ISBN("978-0132350884")))
    book_items.save(BookItem("BI002", ISBN("978-0132350884")))
    borrower_accounts.save(BorrowerAccount("ST123", BorrowerType.STUDENT, borrowing_limit=3))

    # Dependency Injection: concrete adapters are chosen here, at the edge.
    borrow_book = BorrowBookApplicationService(
        book_items,
        borrower_accounts,
        LoanDueDateService(),
        BookBorrowedHandler(borrower_accounts),
    )
    return_book = ReturnBookApplicationService(book_items, borrower_accounts)

    print("Library Borrowing System")
    print("Book items: BI001, BI002   Borrower: ST123 (STUDENT, limit 3)")
    while True:
        action = input("\n[b]orrow, [r]eturn or [q]uit: ").strip().lower()
        if action == "q":
            break
        if action not in ("b", "r"):
            continue

        student_id = input("Student ID: ").strip()
        book_item_id = input("BookItem ID: ").strip()
        if action == "b":
            result = borrow_book.execute(BorrowBookInputDTO(student_id, book_item_id))
            due = f" Due date: {result.due_date}." if result.due_date else ""
            print(f"{result.message}{due}")
        else:
            result = return_book.execute(ReturnBookInputDTO(student_id, book_item_id))
            print(result.message)


if __name__ == "__main__":
    main()
