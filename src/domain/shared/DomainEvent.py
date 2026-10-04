"""The DomainEvent layer supertype."""

from abc import ABC


class DomainEvent(ABC):
    """Base class for something important that happened in the domain."""
