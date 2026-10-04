"""The kinds of borrower the library serves."""

from enum import Enum


class BorrowerType(Enum):
    """Restrict borrowers to the types that have a loan policy."""

    STUDENT = "STUDENT"
    STAFF = "STAFF"
