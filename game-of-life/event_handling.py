from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import threading
import time
from typing import List


class EventType(Enum):
    TIMER_TICK = 1
    UI_QUIT = 2
    UI_STOP = 3
    UI_START = 4


@dataclass(frozen=True)
class Event:
    event_type: EventType
    publisher: EventPublisher


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
        self.subscribers.append(subscriber)

    def publish(self, event_type: EventType) -> None:
        '''
        Publish the event to all subscribers by calling their notify method.
        :param event_type: The type of event to publish.
        :return: None
        '''
        event = Event(event_type, self)
        for sub in self.subscribers:
            sub.notify(event)


class Timer(EventPublisher):
    def __init__(self, interval_sec: float, step_sec: float = 0.1) -> None:
        '''
        Initialize the Timer.
        :param interval_sec: The interval between events in seconds.
        :param step_sec: The mini-step sleep interval in seconds (default: 0.1).
        :return: None
        '''
        super().__init__()
        self.interval = interval_sec
        self.step = step_sec
        self.running = False

    def __enter__(self) -> Timer:
        '''
        Enter the runtime context related to this object. Starts the timer.
        :return: self
        '''
        self.start()
        return self

    def __exit__(self, exc_type: type, exc_val: BaseException, exc_tb) -> None:
        '''
        Exit the runtime context and stop the timer.
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        '''
        self.stop()

    def start(self) -> None:
        '''
        Start the timer event publisher in a background thread.
        :return: None
        '''
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self) -> None:
        '''
        Stop the timer event publisher.
        :return: None
        '''
        self.running = False

    def _run(self) -> None:
        '''
        Internal method to run the timer and publish subscribers at each interval.
        :return: None
        '''
        last_time = time.perf_counter()
        while self.running:
            time.sleep(self.step)
            now = time.perf_counter()
            if now - last_time >= self.interval:
                self.publish(EventType.TIMER_TICK)
                last_time = now
