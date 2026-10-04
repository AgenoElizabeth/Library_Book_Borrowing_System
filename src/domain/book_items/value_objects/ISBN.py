"""The ISBN value object (BR1 - Value Rule)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ISBN:
    """An immutable, valid ISBN-13.

    A value object is defined by its value rather than an identity. Two ISBN
    instances with the same digits compare as equal. Hyphens and spaces are
    removed, then the value must have 13 digits and a correct check digit.
    """

    value: str

    # Named constants communicate domain facts and avoid magic numbers.
    LENGTH = 13
    CHECK_WEIGHTS = (1, 3)

    def __post_init__(self) -> None:
        """Protect BR1: every ISBN in the domain is a valid ISBN-13."""

        digits = self.value.replace("-", "").replace(" ", "")
        if len(digits) != self.LENGTH or not digits.isdigit():
            raise ValueError(f"An ISBN must contain {self.LENGTH} digits: '{self.value}'.")

        total = sum(
            int(digit) * self.CHECK_WEIGHTS[position % 2]
            for position, digit in enumerate(digits)
        )
        if total % 10 != 0:
            raise ValueError(f"The ISBN check digit is not valid: '{self.value}'.")

        object.__setattr__(self, "value", digits)

    @classmethod
    def try_create(cls, value: str) -> ISBN | None:
        """Return a valid ISBN, or ``None`` when the value is invalid."""

        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def create(cls, value: str) -> ISBN:
        """Create an ISBN, raising ``ValueError`` when it is invalid."""

        return cls(value)

    def __str__(self) -> str:
        return self.value
