"""A rich and fault-tolerant console interface for the Library Borrowing System.

Wires dependencies, seeds 100 Computer Science book items and sample borrower accounts,
and provides interactive options to borrow, return, search, list books, and view account statuses.
Handles input normalization, smart ID formatting, and clear error messaging.
"""

import re
import sys
from src.application.borrowing.BookBorrowedHandler import BookBorrowedHandler
from src.application.borrowing.BorrowBookApplicationService import BorrowBookApplicationService
from src.application.borrowing.BorrowBookInputDTO import BorrowBookInputDTO
from src.application.borrowing.ReturnBookApplicationService import ReturnBookApplicationService
from src.application.borrowing.ReturnBookInputDTO import ReturnBookInputDTO
from src.domain.book_items.BookItem import BookItem
from src.domain.book_items.value_objects.BookItemStatus import BookItemStatus
from src.domain.book_items.value_objects.ISBN import ISBN
from src.domain.borrower_accounts.BorrowerAccount import BorrowerAccount
from src.domain.borrower_accounts.services.LoanDueDateService import LoanDueDateService
from src.domain.borrower_accounts.value_objects.BorrowerType import BorrowerType
from src.infrastructure.persistence.InMemoryBookItemRepository import InMemoryBookItemRepository
from src.infrastructure.persistence.InMemoryBorrowerAccountRepository import InMemoryBorrowerAccountRepository


CS_TITLES = [
    "Clean Code: A Handbook of Agile Software Craftsmanship",
    "Introduction to Algorithms (CLRS)",
    "Structure and Interpretation of Computer Programs (SICP)",
    "Design Patterns: Elements of Reusable Object-Oriented Software",
    "The Pragmatic Programmer: Your Journey to Mastery",
    "Artificial Intelligence: A Modern Approach",
    "Computer Systems: A Programmer's Perspective",
    "Operating System Concepts",
    "Computer Networking: A Top-Down Approach",
    "Compilers: Principles, Techniques, and Tools (Dragon Book)",
    "Database System Concepts",
    "Code Complete: A Practical Handbook of Software Construction",
    "The Art of Computer Programming: Fundamental Algorithms",
    "Head First Design Patterns",
    "Refactoring: Improving the Design of Existing Code",
    "Domain-Driven Design: Tackling Complexity in the Heart of Software",
    "Designing Data-Intensive Applications",
    "Computer Architecture: A Quantitative Approach",
    "Modern Operating Systems",
    "Algorithms (Sedgewick & Wayne)",
    "Python Crash Course",
    "Fluent Python: Clear, Concise, and Effective Programming",
    "Learning Python",
    "Programming Pearls",
    "The C Programming Language (K&R)",
    "Effective Java",
    "You Don't Know JS Yet: Scope & Closures",
    "Automate the Boring Stuff with Python",
    "Cracking the Coding Interview",
    "Grokking Algorithms: An Illustrated Guide",
    "Software Engineering at Google",
    "System Design Interview: An Insider's Guide",
    "Clean Architecture: A Craftsman's Guide to Software Structure",
    "Working Effectively with Legacy Code",
    "The Clean Coder: A Code of Conduct for Professional Programmers",
    "Distributed Systems: Principles and Paradigms",
    "Concepts, Techniques, and Models of Computer Programming",
    "Introduction to the Theory of Computation",
    "Pattern-Oriented Software Architecture",
    "Enterprise Integration Patterns",
]


def generate_isbn(index: int) -> ISBN:
    """Generate a valid ISBN-13 string for book seeding."""
    prefix = f"978013235{index:03d}"  # 12 digits
    total = sum(int(d) * (1 if pos % 2 == 0 else 3) for pos, d in enumerate(prefix))
    check_digit = (10 - (total % 10)) % 10
    return ISBN(f"{prefix}{check_digit}")


def seed_data(book_items: InMemoryBookItemRepository, borrower_accounts: InMemoryBorrowerAccountRepository) -> None:
    """Seed 100 Computer Science book items and diverse borrower accounts into memory."""
    for i in range(1, 101):
        book_id = f"BI{i:03d}"
        isbn = generate_isbn(i)
        title = CS_TITLES[(i - 1) % len(CS_TITLES)]
        book_items.save(BookItem(book_id, isbn, title=title))

    for i in range(1, 11):
        student_id = f"ST{i:03d}"
        borrower_accounts.save(BorrowerAccount(student_id, BorrowerType.STUDENT, borrowing_limit=3))
    borrower_accounts.save(BorrowerAccount("ST123", BorrowerType.STUDENT, borrowing_limit=3))

    for i in range(1, 6):
        staff_id = f"SF{i:03d}"
        borrower_accounts.save(BorrowerAccount(staff_id, BorrowerType.STAFF, borrowing_limit=5))


def normalize_book_id(raw_input: str) -> str:
    """Normalize user input to uppercase while preserving standard ID format (e.g. 'bi001' -> 'BI001')."""
    return raw_input.strip().upper()


def normalize_borrower_id(raw_input: str) -> str:
    """Normalize user input to uppercase while preserving standard ID format (e.g. 'st001' -> 'ST001')."""
    return raw_input.strip().upper()



def parse_category_selection(cat_input: str) -> BorrowerType:
    """Parse user category choice (1 for STUDENT, 2 for STAFF)."""
    val = cat_input.strip().lower()
    if val in ("2", "staff", "stf", "f", "sf"):
        return BorrowerType.STAFF
    return BorrowerType.STUDENT


def parse_borrower_type(type_input: str, student_id: str) -> tuple[BorrowerType, int]:
    """Parse borrower category choice with smart fallback based on ID prefix."""
    b_type = parse_category_selection(type_input)
    limit = 5 if b_type == BorrowerType.STAFF else 3
    return b_type, limit


def draw_top(title: str, width: int = 66) -> str:
    """Draw a box top border with a title."""
    header = f"┌─ {title} "
    fill_len = max(0, width - len(header) - 1)
    return header + ("─" * fill_len) + "┐"


def draw_kv(key: str, value: object, width: int = 66) -> str:
    """Draw a formatted key-value row within a box border."""
    val_str = str(value) if value is not None else "N/A"
    content = f"{key:<17}: {val_str}"
    padding = max(0, width - 4 - len(content))
    return f"│ {content}{' ' * padding} │"



def draw_line(text: str, width: int = 66) -> str:
    """Draw a text line within a box border."""
    padding = max(0, width - 4 - len(text))
    return f"│ {text}{' ' * padding} │"


def draw_sep(width: int = 66) -> str:
    """Draw a separator line within a box border."""
    return "├" + ("─" * (width - 2)) + "┤"


def draw_bottom(width: int = 66) -> str:
    """Draw a box bottom border."""
    return "└" + ("─" * (width - 2)) + "┘"



def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    book_items = InMemoryBookItemRepository()
    borrower_accounts = InMemoryBorrowerAccountRepository()

    seed_data(book_items, borrower_accounts)

    borrow_book = BorrowBookApplicationService(
        book_items,
        borrower_accounts,
        LoanDueDateService(),
        BookBorrowedHandler(borrower_accounts),
    )
    return_book = ReturnBookApplicationService(book_items, borrower_accounts)

    print("==================================================================")
    print("      University Library System - Computer Science Section        ")
    print("==================================================================")
    print("System initialized with 100 CS Book Items (BI001 - BI100).")
    print("Available Borrower Accounts:")
    print("  - Students (Limit 3, 14 days): ST001 to ST010, ST123")
    print("  - Staff    (Limit 5, 28 days): SF001 to SF005")

    while True:
        print("\n------------------------------------------------------------------")
        user_choice = input("[b]orrow, [r]eturn, [s]earch, [l]ist books, [a]ccount status, or [q]uit: ").strip().lower()

        if user_choice in ("q", "quit", "exit"):
            print("Exiting Library Borrowing System. Goodbye!")
            break

        if user_choice in ("s", "search"):
            keyword = input("Enter search keyword (title or ID, e.g. 'clean', 'python', 'BI005'): ").strip().lower()
            all_books = [book_items.find_by_id(f"BI{i:03d}") for i in range(1, 101)]
            matches = [b for b in all_books if b and (keyword in b.id.lower() or keyword in b.title.lower())]

            print(f"\n--- Search Results for '{keyword}' ({len(matches)} found) ---")
            if not matches:
                print("No books matched your search keyword.")
            else:
                for b in matches:
                    print(f"ID: {b.id} | Status: {b.status.name:<9} | Title: '{b.title}'")
            continue

        if user_choice in ("l", "list"):
            filter_opt = input("Show [a]ll, [av]ailable only, or [b]orrowed only? (default 'av'): ").strip().lower()
            all_books = [book_items.find_by_id(f"BI{i:03d}") for i in range(1, 101)]
            books = [b for b in all_books if b is not None]

            if filter_opt in ("b", "borrowed"):
                filtered = [b for b in books if b.status.name == "BORROWED"]
            elif filter_opt in ("a", "all"):
                filtered = books
            else:
                filtered = [b for b in books if b.status.name == "AVAILABLE"]

            print(f"\n--- Computer Science Books ({len(filtered)} items) ---")
            for b in filtered[:25]:
                print(f"ID: {b.id} | Status: {b.status.name:<9} | Title: '{b.title}'")
            if len(filtered) > 25:
                print(f"... and {len(filtered) - 25} more books available (BI001 to BI100). Use [s]earch to find specific titles.")
            continue

        if user_choice in ("a", "account"):
            raw_id = input("Enter Borrower ID (e.g. ST001 for Student, SF001 for Staff): ")
            borrower_id = normalize_borrower_id(raw_id)
            if not (borrower_id.startswith("ST") or borrower_id.startswith("SF")):
                print(f"\n❌ INVALID BORROWER ID FORMAT: Borrower ID '{borrower_id}' must start with 'ST' for Students (e.g. ST001) or 'SF' for Staff (e.g. SF001).")
                continue

            account = borrower_accounts.find_by_id(borrower_id)
            if account is None:
                print(f"Error: BorrowerAccount '{borrower_id}' does not exist.")
                print("Valid Borrower IDs: Students (ST001-ST010, ST123), Staff (SF001-SF005).")
            else:
                active_count = len(account.active_borrowings)
                limit = account.borrowing_limit
                remaining = limit - active_count
                b_type_name = account.borrower_type.name

                print(f"\n{draw_top('👤 BORROWER ACCOUNT DETAILS & QUOTA STATUS')}")
                print(draw_kv("Borrower ID", account.id))
                print(draw_kv("Account Type", b_type_name))
                print(draw_kv("Quota Progress", f"{active_count} / {limit} Books ({remaining} remaining)"))
                print(draw_sep())
                if not account.active_borrowings:
                    print(draw_line("  Active Loans   : (None - 0 active loans)"))
                else:
                    print(draw_line(f"  Active Loans ({active_count} on loan):"))
                    for b in account.active_borrowings:
                        book = book_items.find_by_id(b.book_item_id)
                        title = book.title[:26] if book else "Unknown Title"
                        print(draw_line(f"   • [{b.book_item_id}] '{title}' | Due: {b.due_date}"))
                print(draw_sep())
                print(draw_line(" ⚠️ OVERDUE CONSEQUENCES & RULES:"))
                print(draw_line("  • Fine Rate  : $1.00/day (Student) | $0.50/day (Staff)"))
                print(draw_line("  • Penalties  : Overdue accounts are SUSPENDED from borrowing"))
                print(draw_line("                 until all past-due items are returned."))
                print(draw_bottom())
            continue

        if user_choice in ("b", "borrow"):
            # Step 1: Ask if the borrower is a Student or Staff BEFORE anything else is done
            print("\nSelect Borrower Category:")
            print("  [1] Student  (Loan period: 14 days, Quota limit: 3 books)")
            print("  [2] Staff    (Loan period: 28 days, Quota limit: 5 books)")
            cat_choice = input("Is the borrower a Student or Staff member? (1 for Student / 2 for Staff): ")

            chosen_type = parse_category_selection(cat_choice)
            chosen_limit = 5 if chosen_type == BorrowerType.STAFF else 3
            expected_prefix = "SF" if chosen_type == BorrowerType.STAFF else "ST"
            category_name = "Staff" if chosen_type == BorrowerType.STAFF else "Student"
            example_id = "SF001" if chosen_type == BorrowerType.STAFF else "ST001"

            raw_student_id = input(f"Enter Borrower ID (e.g. {example_id}): ")
            student_id = normalize_borrower_id(raw_student_id)

            # Strict Borrower ID Prefix Check
            if not student_id.startswith(expected_prefix):
                print(f"\n❌ INVALID BORROWER ID FORMAT: Borrower ID '{student_id}' does not have the required {category_name} prefix '{expected_prefix}'.")
                print(f"   Transaction cancelled. Please enter a valid {category_name} ID (e.g. {example_id}).")
                continue

            target_account = borrower_accounts.find_by_id(student_id)

            # Check existing account type mismatch
            if target_account is not None and target_account.borrower_type != chosen_type:
                print(f"\n❌ CATEGORY MISMATCH ERROR: BorrowerAccount '{student_id}' is registered as {target_account.borrower_type.name}, but '{chosen_type.name}' category was selected.")
                print(f"   Transaction cancelled. Please select Option [{1 if target_account.borrower_type == BorrowerType.STUDENT else 2}] for {target_account.borrower_type.name}.")
                continue

            if target_account is None:
                print(f"\n[NEW BORROWER REGISTRATION] BorrowerAccount '{student_id}' does not exist.")
                reg_choice = input(f"Register new {chosen_type.name} account '{student_id}' now? (y/n): ").strip().lower()
                if reg_choice in ("y", "yes"):
                    new_account = BorrowerAccount(student_id, chosen_type, borrowing_limit=chosen_limit)
                    borrower_accounts.save(new_account)
                    target_account = new_account
                else:
                    print(f"Error: BorrowerAccount '{student_id}' does not exist. Borrowing cancelled.")
                    continue


            # Step 2: Prompt for BookItem ID
            raw_book_id = input("\nEnter BookItem ID to borrow (e.g. BI001 to BI100): ")
            book_item_id = normalize_book_id(raw_book_id)

            target_book = book_items.find_by_id(book_item_id)
            if target_book is None:
                print(f"Error: BookItem '{book_item_id}' does not exist. (Valid range: BI001 to BI100). Use [s]earch or [l]ist to find books.")
                continue

            # Step 3: Check Book Availability and Borrower Eligibility right after entering Book ID
            active_count = len(target_account.active_borrowings)
            limit = target_account.borrowing_limit
            remaining = limit - active_count
            b_type_name = target_account.borrower_type.name

            is_book_available = target_book.status == BookItemStatus.AVAILABLE
            is_borrower_eligible = remaining > 0

            print(f"\n{draw_top('🔍 CHECKING BOOK AVAILABILITY & BORROWER ELIGIBILITY')}")
            print(draw_kv("Book Item ID", book_item_id))
            print(draw_kv("Book Title", target_book.title[:42]))
            print(draw_kv("Book Status", f"{target_book.status.name} ({'Available' if is_book_available else 'Unavailable'})"))
            print(draw_kv("Borrower ID", f"{student_id} ({b_type_name})"))
            print(draw_kv("Quota Progress", f"{active_count} / {limit} Active Loans ({remaining} remaining)"))
            print(draw_kv("Book Available?", "YES ✅" if is_book_available else "NO ❌ (Currently Borrowed)"))
            print(draw_kv("Borrower Eligible?", "YES ✅" if is_borrower_eligible else "NO ❌ (Quota Limit Reached)"))
            print(draw_bottom())

            if not is_book_available:
                print(f"\n❌ BOOK AVAILABILITY REJECTION: BookItem '{book_item_id}' is currently BORROWED and unavailable.")
                print("   Transaction cancelled. Please choose an AVAILABLE book from inventory.")
                continue

            if not is_borrower_eligible:
                print(f"\n❌ BORROWER ELIGIBILITY REJECTION: Borrower {student_id} has reached their maximum quota limit of {limit} books.")
                print("   Transaction cancelled. Please return an active book before borrowing again.")
                continue

            # Step 4: Execute the actual borrowing
            result = borrow_book.execute(BorrowBookInputDTO(student_id, book_item_id))
            if result.success:
                updated_account = borrower_accounts.find_by_id(student_id)
                new_active = len(updated_account.active_borrowings) if updated_account else active_count + 1
                new_remaining = limit - new_active
                due_str = result.due_date if result.due_date else "N/A"
                fine_rate = "$0.50/day" if b_type_name == "STAFF" else "$1.00/day"

                print(f"\n{draw_top('✅ TRANSACTION SUCCESS: BOOK BORROWED')}")
                print(draw_kv("Borrower ID", f"{student_id} ({b_type_name})"))
                print(draw_kv("Book Item ID", book_item_id))
                print(draw_kv("Book Title", target_book.title[:42]))
                print(draw_kv("Quota Progress", f"{new_active} / {limit} Active Loans ({new_remaining} remaining)"))
                print(draw_sep())
                print(draw_line(" ⏰ DUE DATE NOTIFICATION:"))
                print(draw_line(f"  • Return Deadline : {due_str}"))
                print(draw_line(f"  • Overdue Policy  : Fines accrue at {fine_rate} after deadline."))
                print(draw_line("  • Late Penalty    : Account suspended if return is overdue."))
                print(draw_bottom())
            else:
                print(f"\n❌ FAILED TO BORROW: {result.message}")


        elif user_choice in ("r", "return"):
            raw_student_id = input("Enter Borrower ID (e.g. ST001, SF001): ")
            raw_book_id = input("Enter BookItem ID (e.g. BI001 to BI100): ")

            student_id = normalize_borrower_id(raw_student_id)
            book_item_id = normalize_book_id(raw_book_id)

            if not (student_id.startswith("ST") or student_id.startswith("SF")):
                print(f"\n❌ INVALID BORROWER ID FORMAT: Borrower ID '{student_id}' must start with 'ST' for Students (e.g. ST001) or 'SF' for Staff (e.g. SF001).")
                continue


            target_book = book_items.find_by_id(book_item_id)
            if target_book is None:
                print(f"Error: BookItem '{book_item_id}' does not exist. (Valid range: BI001 to BI100). Use [s]earch or [l]ist to find books.")
                continue

            target_account = borrower_accounts.find_by_id(student_id)
            if target_account is None:
                print(f"Error: BorrowerAccount '{student_id}' does not exist. Available IDs: Students (ST001-ST010, ST123), Staff (SF001-SF005).")
                continue

            result = return_book.execute(ReturnBookInputDTO(student_id, book_item_id))
            if result.success:
                updated_account = borrower_accounts.find_by_id(student_id)
                active_count = len(updated_account.active_borrowings) if updated_account else 0
                limit = updated_account.borrowing_limit if updated_account else 3
                remaining = limit - active_count
                b_type_name = target_account.borrower_type.name
                fine_rate = "$0.50/day" if b_type_name == "STAFF" else "$1.00/day"

                # Step 1: Check if due date had passed or not & send appropriate notification
                if result.days_overdue > 0:
                    print(f"\n{draw_top('⚠️ OFFICIAL NOTIFICATION: OVERDUE FINE ASSESSED')}")
                    print(draw_kv("Borrower ID", student_id))
                    print(draw_kv("Return Status", f"OVERDUE RETURN ({result.days_overdue} Days Late)"))
                    print(draw_kv("Due Date", result.due_date))
                    print(draw_kv("Return Date", result.return_date))
                    print(draw_kv("Fine Rate", f"{fine_rate} ({b_type_name} Category)"))
                    print(draw_kv("Fine Issued", f"${result.fine_amount:.2f} ISSUED TO ACCOUNT"))
                    print(draw_line(" Notification  : Book was returned after the due date."))
                    print(draw_line(f"                 A fine of ${result.fine_amount:.2f} has been charged."))
                    print(f"{draw_bottom()}\n")
                else:
                    print(f"\n{draw_top('📩 OFFICIAL NOTIFICATION: RETURN COMPLIANCE CONFIRMED')}")
                    print(draw_kv("Borrower ID", student_id))
                    print(draw_kv("Return Status", "ON-TIME RETURN (ON OR BEFORE DUE DATE)"))
                    print(draw_kv("Due Date", result.due_date))
                    print(draw_kv("Return Date", result.return_date))
                    print(draw_kv("Fine Accrued", "$0.00 (No Penalties Assessed)"))
                    print(draw_line(" Notification  : Thank you for returning the book on time!"))
                    print(f"{draw_bottom()}\n")

                # Step 2: Show successful return and state that book is available for next borrowing
                print(draw_top("✅ TRANSACTION SUCCESS: BOOK RETURNED"))
                print(draw_kv("Borrower ID", student_id))
                print(draw_kv("Book Item ID", book_item_id))
                print(draw_kv("Book Title", target_book.title[:42]))
                print(draw_kv("Book Status", "AVAILABLE (Restored to Library Inventory)"))
                print(draw_kv("Updated Quota", f"{active_count} / {limit} Active Loans ({remaining} remaining quota)"))
                print(draw_bottom())
            else:
                print(f"\n❌ FAILED TO RETURN: {result.message}")
        else:
            print("Invalid command. Options: [b]orrow, [r]eturn, [s]earch, [l]ist, [a]ccount status, [q]uit.")


if __name__ == "__main__":
    main()
