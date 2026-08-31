from game_of_life.event_handling import Event, EventPublisher, EventSubscriber, EventType, Timer


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


def test_timer_converts_updates_per_second_to_interval() -> None:
    timer = Timer(interval_sec=0.1)
    speed_control = EventPublisher()
    speed_control.attach(timer)

    speed_control.publish(EventType.SPEED_CHANGE, 20.0)

    assert timer.interval == 0.05


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