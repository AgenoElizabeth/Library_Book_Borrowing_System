# Library Borrowing System

A Python project organized using Domain-Driven Design, TDD and Clean Architecture.
It has two connected use cases: **Borrow Book** and **Return Book**. Storage is in memory.

## Layers

- `domain`: aggregates, entities, value objects, the domain service, the domain event, and repository contracts
- `application`: use cases, DTOs, and the event handler
- `infrastructure`: in-memory repository implementations
- `presentation`: the console interface

Dependencies point inward: presentation and infrastructure depend on application/domain, while domain depends on no framework.

Each class has its own file named after the class. A child entity lives in its own
folder inside its aggregate, with its own `value_objects/` when it needs them.

```text
src/
├── domain/
│   ├── shared/
│   │   ├── AggregateRoot.py                 Layer Supertype
│   │   ├── DomainEvent.py                   Layer Supertype
│   │   └── Entity.py                        Layer Supertype
│   ├── book_items/
│   │   ├── BookItem.py                      Aggregate root A (BR2)
│   │   ├── value_objects/
│   │   │   ├── BookItemStatus.py
│   │   │   └── ISBN.py                      Value object (BR1)
│   │   ├── events/
│   │   │   └── BookBorrowed.py              Domain event (BR5)
│   │   └── repositories/
│   │       └── BookItemRepository.py        Repository contract (BR6)
│   └── borrower_accounts/
│       ├── BorrowerAccount.py               Aggregate root B (BR3)
│       ├── borrowings/
│       │   └── Borrowing.py                 Child entity
│       ├── value_objects/
│       │   └── BorrowerType.py
│       ├── services/
│       │   └── LoanDueDateService.py        Domain service (BR4)
│       └── repositories/
│           └── BorrowerAccountRepository.py Repository contract
├── application/
│   └── borrowing/
│       ├── BorrowBookApplicationService.py  Main use case
│       ├── ReturnBookApplicationService.py  Second use case
│       ├── BookBorrowedHandler.py           Event handler (BR5)
│       ├── DomainEventHandler.py            Handler contract
│       ├── BorrowBookInputDTO.py
│       ├── BorrowBookOutputDTO.py
│       ├── ReturnBookInputDTO.py
│       └── ReturnBookOutputDTO.py
├── infrastructure/
│   └── persistence/
│       ├── InMemoryBookItemRepository.py
│       └── InMemoryBorrowerAccountRepository.py
└── presentation/
    └── console.py                           Entry point and dependency wiring
```

## Run locally

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Test

```bash
pytest
```

Saved test output: [evidence/test_output.txt](evidence/test_output.txt).

If ROS (or another tool) adds its own pytest plugins through `PYTHONPATH`, run
`env -u PYTHONPATH pytest` instead.

## Run the console application

```bash
python -m src.presentation.console
```

## Business rules and tests

| Rule | Type | Statement | Responsible | Tests |
|------|------|-----------|-------------|-------|
| BR1 | Value | ISBN must be a valid ISBN-13 | `ISBN` value object | T1, T2 |
| BR2 | Identity/State | A BookItem can be borrowed only when AVAILABLE | `BookItem` aggregate root | T3, T4 |
| BR3 | Invariant | Active borrowings must not exceed the borrowing limit | `BorrowerAccount` aggregate root | T5, T8 |
| BR4 | Cross-concept | Due date = borrowing date + loan days for the borrower type | `LoanDueDateService` | T6 |
| BR5 | Follow-up | After a successful borrow, the borrowing is recorded in BorrowerAccount | `BookBorrowed` + `BookBorrowedHandler` | T7, T8 |
| BR6 | Lookup | The BookItem must exist before borrowing continues | `BookItemRepository` + `BorrowBookApplicationService` | T7 |

## Design decisions

- **ISBN (BR1):** only ISBN-13 is accepted. Hyphens and spaces are removed, then the value
  must be 13 digits with a correct check digit.
- **Loan policy (BR4):** STUDENT borrowers get 14 days and STAFF borrowers get 28 days. A
  different policy can be passed into `LoanDueDateService` without changing the class.
- **BR3 is checked in one place.** BorrowerAccount checks the limit when BookBorrowedHandler
  asks it to record the borrowing. The application service does not check it first, so T8
  tests the real rejection path through the full use case.
- **Consistent state after rejection.** When BorrowerAccount rejects the borrowing, the
  application service does not save the BookItem, so it stays AVAILABLE. Repositories
  return copies, so changes reach storage only through `save`.
- **Validation before mutation.** Aggregates check their rules before they change state,
  so a rejected operation leaves them unchanged.
- **Errors:** business rule violations raise `ValueError` with a clear message. The
  application services turn them into a failed output DTO.
- **Layer Supertype:** implemented in `domain/shared`. `Entity` gives identity-based
  equality, `AggregateRoot` records Domain Events, and `DomainEvent` is the event base class.
- **Factory:** not used. Creating BookItem and BorrowerAccount is simple enough for constructors.
- **Dependency Injection:** repositories, the domain service, the event handler and the
  clock are passed into `BorrowBookApplicationService`. They are wired in `presentation/console.py`.

## TDD evidence (T3)

1. **RED:** T3 was written first while `BookItem.borrow()` was an empty stub, so the test
   failed: [evidence/tdd_t3_red.txt](evidence/tdd_t3_red.txt)
2. **GREEN:** the minimum code was added (set the status to BORROWED), and the test passed:
   [evidence/tdd_t3_green.txt](evidence/tdd_t3_green.txt)
3. **REFACTOR:** the BR2 check and the BookBorrowed event were added, and the test still
   passed: [evidence/tdd_t3_refactor.txt](evidence/tdd_t3_refactor.txt)

## AI disclosure

AI tools were used to assist with understanding DDD concepts, structuring the coursework
design, and reviewing implementation ideas. All final design and implementation decisions
were reviewed and understood by the group.
