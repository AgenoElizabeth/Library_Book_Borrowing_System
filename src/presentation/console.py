"""A rich and fault-tolerant console interface for the Library Borrowing System.

Wires dependencies, seeds 100 Computer Science book items and sample borrower accounts,
and provides interactive options to borrow, return, search, list books, and view account statuses.
Handles input normalization, smart ID formatting, and clear error messaging.
"""

import re
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
    """Convert flexible input like '1', 'bi1', 'BI5' into standard 'BI001' format."""
    val = raw_input.strip().upper()
    if val.isdigit():
        return f"BI{int(val):03d}"
    match = re.match(r"^BI(\d+)$", val)
    if match:
        return f"BI{int(match.group(1)):03d}"
    return val


def normalize_borrower_id(raw_input: str) -> str:
    """Convert flexible input like '1', 'st1', 'sf2' into standard 'ST001' or 'SF002' format."""
    val = raw_input.strip().upper()
    if val.isdigit():
        return f"ST{int(val):03d}"
    match_st = re.match(r"^ST(\d+)$", val)
    if match_st:
        return f"ST{int(match_st.group(1)):03d}"
    match_sf = re.match(r"^SF(\d+)$", val)
    if match_sf:
        return f"SF{int(match_sf.group(1)):03d}"
    return val


def parse_borrower_type(type_input: str, student_id: str) -> tuple[BorrowerType, int]:
    """Parse borrower category choice with smart fallback based on ID prefix."""
    val = type_input.strip().lower()
    if val in ("2", "staff", "stf", "f", "sf"):
        return BorrowerType.STAFF, 5
    if val in ("1", "student", "st", "s"):
        return BorrowerType.STUDENT, 3

    # Smart fallback based on Borrower ID prefix (SF -> STAFF, ST -> STUDENT)
    if student_id.upper().startswith("SF"):
        return BorrowerType.STAFF, 5
    return BorrowerType.STUDENT, 3


def main() -> None:
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
            raw_id = input("Enter Borrower ID (e.g. ST001, SF001, ST123): ")
            borrower_id = normalize_borrower_id(raw_id)
            account = borrower_accounts.find_by_id(borrower_id)
            if account is None:
                print(f"Error: BorrowerAccount '{borrower_id}' does not exist.")
                print("Valid Borrower IDs: Students (ST001-ST010, ST123), Staff (SF001-SF005).")
            else:
                active_count = len(account.active_borrowings)
                limit = account.borrowing_limit
                remaining = limit - active_count
                b_type_name = account.borrower_type.name
                
                print(f"\n┌──────────────────────────────────────────────────────────────────┐")
                print(f"│ 👤 BORROWER ACCOUNT DETAILS & QUOTA STATUS                        │")
                print(f"├──────────────────────────────────────────────────────────────────┤")
                print(f"│  Borrower ID   : {account.id:<48} │")
                print(f"│  Account Type  : {b_type_name:<48} │")
                print(f"│  Quota Progress: {active_count} / {limit} Books Borrowed ({remaining} quota remaining){' ' * (18 - len(str(active_count)) - len(str(limit)) - len(str(remaining)))} │")
                print(f"├──────────────────────────────────────────────────────────────────┤")
                if not account.active_borrowings:
                    print(f"│  Active Borrowings: (None - 0 active loans){' ' * 24} │")
                else:
                    print(f"│  Active Borrowings ({active_count} on loan):{' ' * 36} │")
                    for b in account.active_borrowings:
                        book = book_items.find_by_id(b.book_item_id)
                        title = book.title[:28] if book else "Unknown Title"
                        print(f"│   • [{b.book_item_id}] '{title}' | Due: {b.due_date}{' ' * 4} │")
                print(f"├──────────────────────────────────────────────────────────────────┤")
                print(f"│ ⚠️ OVERDUE CONSEQUENCES & RULES:                                 │")
                print(f"│  • Fine Rate  : $1.00/day (Student) | $0.50/day (Staff)          │")
                print(f"│  • Penalties  : Accounts with overdue books are SUSPENDED from    │")
                print(f"│                 borrowing further items until cleared.           │")
                print(f"└──────────────────────────────────────────────────────────────────┘")
            continue

        if user_choice not in ("b", "borrow", "r", "return"):
            print("Invalid command. Options: [b]orrow, [r]eturn, [s]earch, [l]ist, [a]ccount status, [q]uit.")
            continue

        raw_student_id = input("Enter Borrower ID (e.g. ST001, ST123, SF001): ")
        raw_book_id = input("Enter BookItem ID (e.g. BI001 to BI100 or '1'): ")

        student_id = normalize_borrower_id(raw_student_id)
        book_item_id = normalize_book_id(raw_book_id)

        target_book = book_items.find_by_id(book_item_id)
        if target_book is None:
            print(f"Error: BookItem '{book_item_id}' does not exist. (Valid range: BI001 to BI100). Use [s]earch or [l]ist to find books.")
            continue

        target_account = borrower_accounts.find_by_id(student_id)
        if target_account is None:
            if user_choice in ("b", "borrow"):
                print(f"\n[NEW BORROWER REGISTRATION] BorrowerAccount '{student_id}' does not exist.")
                reg_choice = input(f"Would you like to register new borrower '{student_id}' now? (y/n): ").strip().lower()
                if reg_choice in ("y", "yes"):
                    print("\nSelect Borrower Category:")
                    print("  [1] Student  (Loan period: 14 days, Quota limit: 3 books)")
                    print("  [2] Staff    (Loan period: 28 days, Quota limit: 5 books)")
                    type_input = input("Enter choice (1 for Student / 2 for Staff): ")
                    
                    b_type, limit = parse_borrower_type(type_input, student_id)
                    loan_days = 28 if b_type == BorrowerType.STAFF else 14
                    
                    # Create and save new borrower account
                    new_account = BorrowerAccount(student_id, b_type, borrowing_limit=limit)
                    borrower_accounts.save(new_account)
                    target_account = new_account
                    
                    # Send structured eligibility notification
                    print("\n┌──────────────────────────────────────────────────────────────────┐")
                    print("│ 📩 OFFICIAL NOTIFICATION: NEW BORROWER REGISTRATION              │")
                    print("├──────────────────────────────────────────────────────────────────┤")
                    print(f"│  Borrower ID   : {student_id:<48} │")
                    print(f"│  Account Type  : {b_type.name:<48} │")
                    print(f"│  Loan Period   : {loan_days} Days per Book{' ' * 31} │")
                    print(f"│  Quota Limit   : {limit} Active Borrowings{' ' * 30} │")
                    print(f"│  Status        : ACTIVE & ELIGIBLE TO BORROW                     │")
                    print("└──────────────────────────────────────────────────────────────────┘\n")
                else:
                    print(f"Error: BorrowerAccount '{student_id}' does not exist. Borrowing cancelled.")
                    continue
            else:
                print(f"Error: BorrowerAccount '{student_id}' does not exist. Available IDs: Students (ST001-ST010, ST123), Staff (SF001-SF005).")
                continue

        if user_choice in ("b", "borrow"):
            result = borrow_book.execute(BorrowBookInputDTO(student_id, book_item_id))
            if result.success:
                updated_account = borrower_accounts.find_by_id(student_id)
                active_count = len(updated_account.active_borrowings) if updated_account else 1
                limit = updated_account.borrowing_limit if updated_account else 3
                remaining = limit - active_count
                b_type_name = target_account.borrower_type.name
                due_str = str(result.due_date) if result.due_date else "N/A"
                fine_rate = "$0.50/day" if b_type_name == "STAFF" else "$1.00/day"
                
                print("\n┌──────────────────────────────────────────────────────────────────┐")
                print("│ ✅ TRANSACTION SUCCESS: BOOK BORROWED                            │")
                print("├──────────────────────────────────────────────────────────────────┤")
                print(f"│  Borrower ID   : {student_id} ({b_type_name}){' ' * (41 - len(student_id) - len(b_type_name))} │")
                print(f"│  Book Item ID  : {book_item_id:<48} │")
                title_disp = target_book.title[:45]
                print(f"│  Book Title    : '{title_disp}'{' ' * (45 - len(title_disp))} │")
                print(f"│  Quota Progress: {active_count} / {limit} Active Loans ({remaining} remaining){' ' * (18 - len(str(active_count)) - len(str(limit)) - len(str(remaining)))} │")
                print(f"├──────────────────────────────────────────────────────────────────┤")
                print(f"│ ⏰ DUE DATE NOTIFICATION:                                         │")
                print(f"│  • Return Deadline : {due_str:<45} │")
                print(f"│  • Overdue Policy  : Fines accrue at {fine_rate} after deadline.    │")
                print(f"│  • Late Penalty    : Account suspended if return is overdue.     │")
                print("└──────────────────────────────────────────────────────────────────┘")
            else:
                print(f"\n❌ FAILED TO BORROW: {result.message}")
        else:
            result = return_book.execute(ReturnBookInputDTO(student_id, book_item_id))
            if result.success:
                updated_account = borrower_accounts.find_by_id(student_id)
                active_count = len(updated_account.active_borrowings) if updated_account else 0
                limit = updated_account.borrowing_limit if updated_account else 3
                remaining = limit - active_count
                
                print("\n┌──────────────────────────────────────────────────────────────────┐")
                print("│ ✅ TRANSACTION SUCCESS: BOOK RETURNED                            │")
                print("├──────────────────────────────────────────────────────────────────┤")
                print(f"│  Borrower ID   : {student_id:<48} │")
                print(f"│  Book Item ID  : {book_item_id:<48} │")
                title_disp = target_book.title[:45]
                print(f"│  Book Title    : '{title_disp}'{' ' * (45 - len(title_disp))} │")
                print(f"│  Book Status   : AVAILABLE (Restored to Library Inventory)       │")
                print(f"│  Updated Quota : {active_count} / {limit} Active Loans ({remaining} remaining quota){' ' * (12 - len(str(active_count)) - len(str(limit)) - len(str(remaining)))} │")
                print("└──────────────────────────────────────────────────────────────────┘")
            else:
                print(f"\n❌ FAILED TO RETURN: {result.message}")


if __name__ == "__main__":
    main()
