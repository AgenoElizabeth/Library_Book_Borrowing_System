"""Tests for presentation layer console helper functions."""

from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType
from src.infrastructure.persistence.InMemoryBookItemRepository import InMemoryBookItemRepository
from src.infrastructure.persistence.InMemoryBorrowerAccountRepository import InMemoryBorrowerAccountRepository
from src.presentation.console import (
    draw_bottom,
    draw_kv,
    draw_line,
    draw_sep,
    draw_top,
    generate_isbn,
    normalize_book_id,
    normalize_borrower_id,
    parse_borrower_type,
    parse_category_selection,
    seed_data,
)


def test_normalize_book_id():
    assert normalize_book_id("bi001") == "BI001"
    assert normalize_book_id("BI010") == "BI010"
    assert normalize_book_id("BI100") == "BI100"


def test_normalize_borrower_id():
    assert normalize_borrower_id("st001") == "ST001"
    assert normalize_borrower_id("sf003") == "SF003"
    assert normalize_borrower_id("ST123") == "ST123"



def test_generate_isbn():
    isbn = generate_isbn(1)
    assert len(isbn.value) == 13
    assert isbn.value.startswith("978013235")



def test_seed_data():
    book_repo = InMemoryBookItemRepository()
    account_repo = InMemoryBorrowerAccountRepository()
    seed_data(book_repo, account_repo)

    assert book_repo.find_by_id("BI001") is not None
    assert book_repo.find_by_id("BI100") is not None
    assert account_repo.find_by_id("ST001") is not None
    assert account_repo.find_by_id("SF001") is not None
    assert account_repo.find_by_id("ST123") is not None


def test_parse_category_selection():
    assert parse_category_selection("1") == BorrowerType.STUDENT
    assert parse_category_selection("student") == BorrowerType.STUDENT
    assert parse_category_selection("2") == BorrowerType.STAFF
    assert parse_category_selection("staff") == BorrowerType.STAFF


def test_parse_borrower_type():
    b_type, limit = parse_borrower_type("1", "ST001")
    assert b_type == BorrowerType.STUDENT
    assert limit == 3

    b_type, limit = parse_borrower_type("2", "SF001")
    assert b_type == BorrowerType.STAFF
    assert limit == 5


def test_box_drawing_helpers():
    top = draw_top("Test Title", width=66)
    assert top.startswith("┌─ Test Title ")
    assert top.endswith("┐")

    kv = draw_kv("Key", "Value", width=66)
    assert kv.startswith("│ Key")
    assert kv.endswith("│")

    line = draw_line("Some Text", width=66)
    assert line.startswith("│ Some Text")
    assert line.endswith("│")

    sep = draw_sep(width=66)
    assert sep == "├" + ("─" * 64) + "┤"

    bottom = draw_bottom(width=66)
    assert bottom == "└" + ("─" * 64) + "┘"
