"""The contract every domain event handler follows."""

from typing import Protocol

from src.domain.shared.DomainEvent import DomainEvent


class DomainEventHandler(Protocol):
    """Anything that can react to a Domain Event in-process.

    Application services depend on this contract instead of a concrete
    handler class (Dependency Inversion).
    """

    def handle(self, event: DomainEvent) -> None: ...
