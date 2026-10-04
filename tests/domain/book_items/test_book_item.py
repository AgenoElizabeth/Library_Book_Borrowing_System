from datetime import date

import pytest

from src.domain.book_items.BookItem import BookItem
from src.domain.book_items.value_objects.BookItemStatus import BookItemStatus
from src.domain.book_items.value_objects.ISBN import ISBN


def available_book_item() -> BookItem:
    return BookItem("BI001", ISBN("978-0132350884"))


def test_t3_an_available_book_item_can_be_borrowed() -> None:
    # T3 - BR2: an AVAILABLE BookItem becomes BORROWED.
    # Arrange
    book_item = available_book_item()

    # Act
    book_item.borrow("ST123", date(2026, 10, 1), date(2026, 10, 15))

    # Assert
    assert book_item.status is BookItemStatus.BORROWED


def test_t4_a_borrowed_book_item_cannot_be_borrowed_again() -> None:
    # T4 - BR2 (rejection): a BORROWED BookItem stays BORROWED.
    # Arrange
    book_item = available_book_item()
    book_item.borrow("ST123", date(2026, 10, 1), date(2026, 10, 15))

    # Act
    with pytest.raises(ValueError) as exception_info:
        book_item.borrow("ST456", date(2026, 10, 2), date(2026, 10, 16))

    # Assert
    assert "BookItem BI001 is already borrowed" in str(exception_info.value)
    assert book_item.status is BookItemStatus.BORROWED
