from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import time
from typing import Any, List


class EventType(Enum):
    UI_QUIT = 1
    UI_STOP = 2
    UI_START = 3
    SPEED_CHANGE = 4


@dataclass(frozen=True)
class Event:
    event_type: EventType
    payload: Any = None


class EventSubscriber(ABC):
    @abstractmethod
    def notify(self, event: Event) -> None:
        '''
        Called by EventPublisher on each event.
        :param event: The event to handle.
        :return: None
        '''
        pass


class EventPublisher:
    def __init__(self) -> None:
        '''
        Initialize the EventPublisher with an empty list of subscribers.
        :return: None
        '''
        self.subscribers: List[EventSubscriber] = []

    def attach(self, subscriber: EventSubscriber) -> None:
        '''
        Attach a subscriber to receive events.
        :param subscriber: The EventSubscriber to attach.
        :return: None
        '''
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)

    def detach(self, subscriber: EventSubscriber) -> None:
        '''
        Stop a subscriber from receiving events.
        :param subscriber: The EventSubscriber to detach.
        :return: None
        '''
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def publish(self, event_type: EventType, payload: Any = None) -> None:
        '''
        Publish the event to all subscribers by calling their notify method.
        :param event_type: The type of event to publish.
        :param payload: Optional event data.
        :return: None
        '''
        event = Event(event_type, payload)
        # Keep delivery stable if a notification callback attaches or detaches subscribers.
        for sub in self.subscribers.copy():
            sub.notify(event)


class Clock(ABC):
    """Provide monotonic time for scheduling simulation updates."""

    @abstractmethod
    def now(self) -> float:
        """Return the current monotonic time in seconds."""
        pass


class SystemClock(Clock):
    """Adapt the system performance counter to the simulation clock interface."""

    def now(self) -> float:
        """Return the current value of the system performance counter."""
        return time.perf_counter()


class TickSource(ABC):
    """Define how the controller checks whether a simulation update is due."""

    @abstractmethod
    def poll(self) -> bool:
        """Return whether a simulation tick is due."""
        pass


class Ticker(EventSubscriber, TickSource):
    """Schedule simulation ticks and react to requested speed changes."""

    def __init__(self, interval_sec: float, clock: Clock) -> None:
        """Initialize the ticker.

        :param interval_sec: The interval between ticks in seconds.
        :param clock: The monotonic clock used to measure elapsed time.
        """
        self.interval = interval_sec
        self.clock = clock
        self._last_tick = clock.now()

    def notify(self, event: Event) -> None:
        """Update the simulation interval when a speed-change event arrives.

        :param event: An application event, optionally containing updates per second.
        """
        if event.event_type == EventType.SPEED_CHANGE:
            speed = event.payload
            if speed > 0:  # Prevent division by zero
                self.interval = 1.0 / speed  # Convert speed (updates/sec) to interval (sec)

    def poll(self) -> bool:
        """Check whether enough simulation time has elapsed for another tick.

        :return: True once per elapsed interval; otherwise False.
        """
        now = self.clock.now()
        if now - self._last_tick < self.interval:
            return False

        self._last_tick = now
        return True
