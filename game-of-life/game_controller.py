from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import pygame

from event_handling import Event, EventSubscriber, EventType
from game_logic import GameOfLifeRuleset
from singleton_subscriber_meta import SingletonSubscriberMeta
from ui import UI


class GameController(EventSubscriber, metaclass=SingletonSubscriberMeta):
    def __init__(self) -> None:
        '''
        Initialize the GameController with empty game logic, board state, and UI. Set startup state to running.
        :return: None
        '''
        self.game_logic = None
        self.board_state = None
        self.ui = None

        self.ui_render_needed = False
        self.game_state: GameState = GameRunning()


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
                self.board_state, self.ui_render_needed = self.game_state.handle_timer_tick(
                    self.game_logic, self.board_state)
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
        running = True
        self.ui.render(self.board_state)
        while running:
            self.ui.run()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.ui.buttons:
                        if button.x <= event.pos[0] <= button.x + button.width \
                                and button.y <= event.pos[1] <= button.y + button.height:
                            if button.name == "stop":
                                self.game_state = GameStopped()
                            # Add more button actions here
                            break
                    # Only handle button clicks, do not break for non-button clicks
            if self.ui_render_needed:
                self.ui.render(self.board_state)
                self.ui_render_needed = False
        pygame.quit()


class GameState(ABC):
    '''
    Abstract base class (interface) for game operational state.
    '''

    @abstractmethod
    def handle_timer_tick(self, game_logic: GameOfLifeRuleset, board_state: np.ndarray) -> tuple[np.ndarray, bool]:
        pass


class GameStopped(GameState):
    '''
    Represents the stopped state of the game.
    This state indicates that the game is not running.
    '''

    def handle_timer_tick(self, game_logic: GameOfLifeRuleset, board_state: np.ndarray) -> tuple[np.ndarray, bool]:
        return board_state, False


class GameRunning(GameState):
    '''
    Represents the running state of the game.
    This state indicates that the game is currently active and processing.
    '''

    def handle_timer_tick(self, game_logic: GameOfLifeRuleset, board_state: np.ndarray) -> tuple[np.ndarray, bool]:
        return game_logic.next_generation(board_state), True
