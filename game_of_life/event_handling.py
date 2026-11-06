"""Publish application events and schedule simulation updates."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class EventType(Enum):
    """Identify events exchanged between the UI and application."""

    UI_QUIT = 1
    UI_STOP = 2
    UI_START = 3
    SPEED_CHANGE = 4


@dataclass(frozen=True)
class Event:
    """Carry an event type and optional associated data."""

    event_type: EventType
    payload: Any = None


class EventSubscriber(ABC):
    """Define the interface for objects that receive published events."""

    @abstractmethod
    def notify(self, event: Event) -> None:
        """Handle an event published to this subscriber.

        Args:
            event: The event to handle.

        Returns:
            None.
        """

class EventPublisher:
    """Manage subscribers and deliver events to them."""

    def __init__(self) -> None:
        """Initialize the publisher with no subscribers.

        Args:
            None.

        Returns:
            None.
        """
        self.subscribers: list[EventSubscriber] = []

    def attach(self, subscriber: EventSubscriber) -> None:
        """Attach a subscriber to receive events.

        Args:
            subscriber: The subscriber to attach.

        Returns:
            None.
        """
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)

    def detach(self, subscriber: EventSubscriber) -> None:
        """Stop a subscriber from receiving events.

        Args:
            subscriber: The subscriber to detach.

        Returns:
            None.
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def publish(self, event_type: EventType, payload: Any = None) -> None:
        """Publish an event to all attached subscribers.

        Args:
            event_type: The type of event to publish.
            payload: Optional event data.

        Returns:
            None.
        """
        event = Event(event_type, payload)
        # Keep delivery stable if a notification callback attaches or detaches subscribers.
        for sub in self.subscribers.copy():
            sub.notify(event)


class Clock(ABC):
    """Provide monotonic time for scheduling simulation updates."""

    @abstractmethod
    def now(self) -> float:
        """Return the current monotonic time.

        Args:
            None.

        Returns:
            Current monotonic time in seconds.
        """


class SystemClock(Clock):
    """Adapt the system performance counter to the simulation clock interface."""

    def now(self) -> float:
        """Return the current system performance counter value.

        Args:
            None.

        Returns:
            Current monotonic time in seconds.
        """
        return time.perf_counter()


class TickSource(ABC):
    """Define how the controller checks whether a simulation update is due."""

    @abstractmethod
    def poll(self) -> bool:
        """Check whether a simulation tick is due.

        Args:
            None.

        Returns:
            Whether the next simulation update is due.
        """


class Ticker(EventSubscriber, TickSource):
    """Schedule simulation ticks and react to requested speed changes."""

    def __init__(self, interval_sec: float, clock: Clock) -> None:
        """Initialize the ticker with an update interval and clock.

        Args:
            interval_sec: The interval between ticks in seconds.
            clock: The monotonic clock used to measure elapsed time.

        Returns:
            None.
        """
        self.interval = interval_sec
        self.clock = clock
        self._last_tick = clock.now()

    def notify(self, event: Event) -> None:
        """Update the simulation interval when a speed-change event arrives.

        Args:
            event: An application event, optionally containing updates per second.

        Returns:
            None.
        """
        if event.event_type == EventType.SPEED_CHANGE:
            speed = event.payload
            self.interval = 1.0 / speed  # Convert speed (updates/sec) to interval (sec)

    def poll(self) -> bool:
        """Check whether enough simulation time has elapsed for another tick.

        Returns:
            True once per elapsed interval; otherwise, False.

        Args:
            None.
        """
        now = self.clock.now()
        if now - self._last_tick < self.interval:
            return False

        self._last_tick = now
        return True
