"""The Entity layer supertype."""

from abc import ABC, abstractmethod
from collections.abc import Hashable


class Entity(ABC):
    """Base class for every object that is identified by an identity.

    Two entities are equal when they are the same type and have the same id,
    even when their other attributes are different.
    """

    @abstractmethod
    def __init__(self, entity_id: Hashable) -> None:
        self._id = entity_id

    @property
    def id(self) -> Hashable:
        """Return the identity of this entity."""

        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False

        if type(self) is not type(other):
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
