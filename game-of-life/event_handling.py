from abc import ABC, abstractmethod
import threading
import time
from typing import List

class EventSubscriber(ABC):
    @abstractmethod
    def on_event(self) -> None:
        '''
        Called by EventPublisher on each event.
        :return: None
        '''
        pass

class EventPublisher(ABC):
    def __init__(self) -> None:
        '''
        Initialize the EventPublisher with an empty list of subscribers.
        :return: None
        '''
        self.subscribers: List[EventSubscriber] = []

    def subscribe(self, subscriber: EventSubscriber) -> None:
        '''
        Add a subscriber to the list.
        :param subscriber: An instance of EventSubscriber.
        :return: None
        '''
        self.subscribers.append(subscriber)

    def notify(self) -> None:
        '''
        Notify all subscribers by calling their on_event method.
        :return: None
        '''
        for sub in self.subscribers:
            sub.on_event()

class TimerEventPublisher(EventPublisher):
    def __init__(self, interval_sec: float, step_sec: float = 0.1) -> None:
        '''
        Initialize the TimerEventPublisher.
        :param interval_sec: The interval between events in seconds.
        :param step_sec: The mini-step sleep interval in seconds (default: 0.1).
        :return: None
        '''
        super().__init__()
        self.interval: float = interval_sec
        self.step: float = step_sec
        self.running: bool = False

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
        Internal method to run the timer and notify subscribers at each interval.
        :return: None
        '''
        last_time = time.perf_counter()
        while self.running:
            time.sleep(self.step)
            now = time.perf_counter()
            if now - last_time >= self.interval:
                self.notify()
                last_time = now
