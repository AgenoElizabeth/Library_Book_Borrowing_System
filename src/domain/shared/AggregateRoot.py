"""The AggregateRoot layer supertype."""

from abc import abstractmethod
from collections.abc import Hashable

from src.domain.shared.DomainEvent import DomainEvent
from src.domain.shared.Entity import Entity


class AggregateRoot(Entity):
    """Base class for aggregate roots.

    An aggregate root records the Domain Events it raises. The application
    layer reads them after the operation and dispatches them to handlers.
    """

    @abstractmethod
    def __init__(self, entity_id: Hashable) -> None:
        super().__init__(entity_id)
        self._domain_events: list[DomainEvent] = []

    def _raise_domain_event(self, domain_event: DomainEvent) -> None:
        self._domain_events.append(domain_event)

    def get_domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()
