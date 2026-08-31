from game_of_life.event_handling import Event, EventPublisher, EventType, Timer


class SpeedControl(EventPublisher):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value


def test_timer_converts_updates_per_second_to_interval() -> None:
    timer = Timer(interval_sec=0.1)
    speed_control = SpeedControl(value=20.0)

    timer.notify(Event(EventType.SPEED_CHANGE, speed_control))

    assert timer.interval == 0.05