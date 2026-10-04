import pytest

from src.domain.book_items.value_objects.ISBN import ISBN


def test_t1_a_valid_isbn_is_accepted() -> None:
    # T1 - BR1: a valid ISBN-13 is accepted.
    # Arrange
    value = "978-0132350884"

    # Act
    isbn = ISBN.create(value)

    # Assert
    assert isbn.value == "9780132350884"


def test_t2_an_isbn_with_a_wrong_check_digit_is_rejected() -> None:
    # T2 - BR1 (rejection): an invalid ISBN never enters the domain.
    # Arrange
    value = "978-0132350885"

    # Act
    with pytest.raises(ValueError) as exception_info:
        ISBN.create(value)

    # Assert
    assert "The ISBN check digit is not valid" in str(exception_info.value)
