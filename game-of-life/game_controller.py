from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import threading

from event_handling import Event, EventSubscriber, EventType
from game_logic import GameOfLifeRuleset
from singleton_subscriber_meta import SingletonSubscriberMeta
from ui import UI


tick_event = threading.Event()
tick_event.clear()


class GameController(EventSubscriber, metaclass=SingletonSubscriberMeta):
    def __init__(self) -> None:
        '''
        Initialize the GameController with empty game logic, board state, and UI. Set startup state to running.
        :return: None
        '''
        self.game_logic = None
        self.board_state = None
        self.ui = None

        self.running = False
        self.game_state: GameState = GameStopped(self)


    def set_board_state(self, state: np.ndarray) -> None:
        '''
        Set the current game state. This method should be used to set initial state of singleton.
        :set board_state: The current game state to render.
        :return: None
        '''
        self.board_state = state

    def assign_game_logic(self, game_logic: GameOfLifeRuleset) -> None:
        '''
        Set the game logic (ruleset) to use.
        :param game_logic: The game logic (ruleset) to use (must implement GameOfLifeRuleset).
        :return: None
        '''
        self.game_logic = game_logic

    def assign_ui(self, ui: UI) -> None:
        '''
        Set the UI object to use.
        :param ui: The UI object to use.
        :return: None
        '''
        self.ui = ui

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
