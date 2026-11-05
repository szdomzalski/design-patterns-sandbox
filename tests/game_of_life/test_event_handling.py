from game_of_life.event_handling import Clock, Event, EventPublisher, EventSubscriber, EventType, Ticker


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


class FakeClock(Clock):
    """Provide manually controlled monotonic time for ticker tests."""

    def __init__(self) -> None:
        """Start the fake clock at zero seconds."""
        self.current_time = 0.0

    def now(self) -> float:
        """Return the current manually controlled time."""
        return self.current_time

    def advance(self, seconds: float) -> None:
        """Advance the clock by the requested number of seconds."""
        self.current_time += seconds


def test_ticker_converts_updates_per_second_to_interval() -> None:
    """A speed event converts updates per second into seconds per update."""
    ticker = Ticker(interval_sec=0.1, clock=FakeClock())
    speed_control = EventPublisher()
    speed_control.attach(ticker)

    speed_control.publish(EventType.SPEED_CHANGE, 20.0)

    assert ticker.interval == 0.05


def test_ticker_reports_tick_only_after_interval() -> None:
    """A ticker becomes due once the configured interval has elapsed."""
    clock = FakeClock()
    ticker = Ticker(interval_sec=1.0, clock=clock)

    assert ticker.poll() is False
    clock.advance(0.99)
    assert ticker.poll() is False
    clock.advance(0.01)
    assert ticker.poll() is True
    assert ticker.poll() is False


def test_attaching_same_subscriber_twice_does_not_duplicate_notifications() -> None:
    """Attaching an existing subscriber again must not deliver an event twice."""
    publisher = EventPublisher()
    subscriber = RecordingSubscriber()
    publisher.attach(subscriber)
    publisher.attach(subscriber)

    publisher.publish(EventType.UI_START)

    assert subscriber.events == [Event(EventType.UI_START)]


def test_detaching_unknown_or_attached_subscriber_is_safe() -> None:
    """Detach is a no-op for unknown subscribers and stops later notifications."""
    publisher = EventPublisher()
    subscriber = RecordingSubscriber()
    publisher.detach(subscriber)
    publisher.attach(subscriber)

    publisher.detach(subscriber)
    publisher.publish(EventType.UI_STOP)

    assert subscriber.events == []