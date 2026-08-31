from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import threading

from .event_handling import Event, EventSubscriber, EventType
from .game_logic import GameOfLifeRuleset
from .ui import UI


tick_event = threading.Event()
tick_event.clear()


class GameController(EventSubscriber):
    def __init__(self, board_state: np.ndarray, game_logic: GameOfLifeRuleset, ui: UI) -> None:
        '''
        Initialize the GameController with its board, game logic, and UI. Set startup state to stopped.
        :param board_state: The initial board state.
        :param game_logic: The ruleset used to calculate each generation.
        :param ui: The UI used to process input and render the board.
        :return: None
        '''
        self.game_logic = game_logic
        self.board_state = board_state
        self.ui = ui

        self.running = False
        self.game_state: GameState = GameStopped(self)

    def notify(self, event: Event) -> None:
        '''
        Handle events from various publishers using pattern matching.
        :param event: The event to handle.
        :return: None
        '''
        match event.event_type:
            case EventType.TIMER_TICK:
                self.tick()
            case EventType.UI_QUIT:
                self.quit()
            case EventType.UI_STOP:
                self.stop()
            case EventType.UI_START:
                self.start()
            case _:
                pass

    def start(self) -> None:
        '''Start or continue the simulation according to its current state.'''
        self.game_state.start()

    def stop(self) -> None:
        '''Stop the simulation according to its current state.'''
        self.game_state.stop()

    def tick(self) -> None:
        '''Handle a simulation tick according to the current state.'''
        self.game_state.tick()

    def quit(self) -> None:
        '''Stop the application loop.'''
        self.running = False

    def _transition_to(self, state: GameState) -> None:
        # States are internal collaborators; application code should request
        # transitions through start() and stop() instead of selecting a state.
        self.game_state = state

    def run(self) -> None:
        '''
        Run the main game loop, handling events and updating the UI.
        :return: None

        The loop continues running until a QUIT event is detected or the timer is stopped.
        Handles mouse button events to interact with UI buttons.
        Renders the UI when an update is needed.
        '''
        self.running = True
        self.ui.render(self.board_state)
        while self.running:
            tick_event.wait()
            self.ui.run()
            self.ui.render(self.board_state)
            tick_event.clear()

        self.ui.close()


class GameState(ABC):
    '''
    Abstract base class (interface) for game operational state.
    '''
    def __init__(self, game: GameController) -> None:
        self.game = game

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def tick(self) -> None:
        pass


class GameStopped(GameState):
    '''
    Represents the stopped state of the game.
    This state indicates that the game is not running.
    '''

    def start(self) -> None:
        self.game._transition_to(GameRunning(self.game))

    def stop(self) -> None:
        pass

    def tick(self) -> None:
        tick_event.set()


class GameRunning(GameState):
    '''
    Represents the running state of the game.
    This state indicates that the game is currently active and processing.
    '''

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self.game._transition_to(GameStopped(self.game))

    def tick(self) -> None:
        self.game.board_state = self.game.game_logic.next_generation(self.game.board_state)
        tick_event.set()
