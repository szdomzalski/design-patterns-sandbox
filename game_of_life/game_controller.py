"""Coordinate simulation state, UI processing, and application events."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .event_handling import Event, EventSubscriber, EventType, TickSource
from .simulation import Simulation
from .ui import UI


class GameController(EventSubscriber):
    """Coordinate UI frames, simulation timing, and operational game state."""

    def __init__(
            self,
            simulation: Simulation,
            ui: UI,
            ticker: TickSource) -> None:
        """Initialize a stopped game with all runtime collaborators.

        Args:
            simulation: The model owning the board and generation strategy.
            ui: The UI used to process input and render the board.
            ticker: The source that determines when simulation ticks are due.

        Returns:
            None.
        """
        self.simulation = simulation
        self.ui = ui
        self.ticker = ticker

        self.running = False
        self.game_state: GameState = GameStopped(self)

    def notify(self, event: Event) -> None:
        """Handle events from publishers using pattern matching.

        Args:
            event: The event to handle.

        Returns:
            None.
        """
        match event.event_type:
            case EventType.UI_QUIT:
                self.quit()
            case EventType.UI_STOP:
                self.stop()
            case EventType.UI_START:
                self.start()
            case _:
                pass

    def start(self) -> None:
        """Start or continue the simulation according to its current state.

        Args:
            None.

        Returns:
            None.
        """
        self.game_state.start()

    def stop(self) -> None:
        """Stop the simulation according to its current state.

        Args:
            None.

        Returns:
            None.
        """
        self.game_state.stop()

    def tick(self) -> None:
        """Handle a simulation tick according to the current state.

        Args:
            None.

        Returns:
            None.
        """
        self.game_state.tick()

    def quit(self) -> None:
        """Stop the application loop.

        Args:
            None.

        Returns:
            None.
        """
        self.running = False

    def _transition_to(self, state: GameState) -> None:
        """Set the active game state.

        Args:
            state: State object to make active.

        Returns:
            None.
        """
        # States are internal collaborators; application code should request
        # transitions through start() and stop() instead of selecting a state.
        self.game_state = state

    def run(self) -> None:
        """Run UI frames until a quit event stops the application.

        The loop processes UI events continuously and advances the simulation
        only when the independently configured ticker reports an update is due.

        Args:
            None.

        Returns:
            None.
        """
        self.running = True
        try:
            self.ui.render(self.simulation.board)
            while self.running:
                self.ui.process_events()
                if not self.running:
                    break
                # The simulation clock decides whether the board advances this frame;
                # it does not control how often UI input and rendering are processed.
                if self.ticker.poll():
                    self.tick()
                self.ui.render(self.simulation.board)
                # The UI clock limits frame frequency independently of simulation speed.
                self.ui.finish_frame()
        finally:
            self.ui.close()


class GameState(ABC):
    """Define state-dependent operations for the game controller."""

    def __init__(self, game: GameController) -> None:
        """Associate this state with its controller.

        Args:
            game: Controller whose state this object represents.

        Returns:
            None.
        """
        self.game = game

    @abstractmethod
    def start(self) -> None:
        """Handle a request to start the game.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def stop(self) -> None:
        """Handle a request to stop the game.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def tick(self) -> None:
        """Handle a simulation tick according to the current state.

        Args:
            None.

        Returns:
            None.
        """


class GameStopped(GameState):
    """Represent a game that is not running."""

    def start(self) -> None:
        """Transition the controller to the running state.

        Args:
            None.

        Returns:
            None.
        """
        self.game._transition_to(GameRunning(self.game))

    def stop(self) -> None:
        """Leave the controller in the stopped state.

        Args:
            None.

        Returns:
            None.
        """

    def tick(self) -> None:
        """Ignore a simulation tick while the game is stopped.

        Args:
            None.

        Returns:
            None.
        """


class GameRunning(GameState):
    """Represent a game that is actively processing simulation ticks."""

    def start(self) -> None:
        """Keep the controller in the running state.

        Args:
            None.

        Returns:
            None.
        """

    def stop(self) -> None:
        """Transition the controller to the stopped state.

        Args:
            None.

        Returns:
            None.
        """
        self.game._transition_to(GameStopped(self.game))

    def tick(self) -> None:
        """Advance the board by one generation while the game is running.

        Args:
            None.

        Returns:
            None.
        """
        self.game.simulation.step()
