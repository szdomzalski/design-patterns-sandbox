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
                self.game_state.handle_timer_tick()
            case EventType.UI_QUIT:
                self.running = False
            case EventType.UI_STOP:
                self.game_state = GameStopped(self)
            case EventType.UI_START:
                self.game_state = GameRunning(self)
            case _:
                pass

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
    def handle_timer_tick(self) -> None:
        pass


class GameStopped(GameState):
    '''
    Represents the stopped state of the game.
    This state indicates that the game is not running.
    '''

    def handle_timer_tick(self) -> None:
        tick_event.set()


class GameRunning(GameState):
    '''
    Represents the running state of the game.
    This state indicates that the game is currently active and processing.
    '''

    def handle_timer_tick(self) -> None:
        self.game.board_state = self.game.game_logic.next_generation(self.game.board_state)
        tick_event.set()
