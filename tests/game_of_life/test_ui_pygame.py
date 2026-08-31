from game_of_life.event_handling import Event, EventSubscriber, EventType
from game_of_life.ui_pygame import PygameUISlider


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


def test_slider_publishes_its_updated_value() -> None:
    # Starting at (0, 0) simplifies the position calculation. A 100 px slider
    # with its 20 px handle has 80 px of horizontal travel.
    slider = PygameUISlider(
        x=0,
        y=0,
        width=100,
        height=20,
        # The value range is 1..11, so its midpoint is 6; start at the minimum.
        min_value=1.0,
        max_value=11.0,
        initial_value=1.0,
        event=EventType.SPEED_CHANGE,
    )
    subscriber = RecordingSubscriber()
    slider.attach(subscriber)

    slider.start_dragging()
    # x=40 is halfway through the 80 px travel, so the slider must publish 6.
    slider.update_drag(40)

    assert subscriber.events == [Event(EventType.SPEED_CHANGE, 6.0)]