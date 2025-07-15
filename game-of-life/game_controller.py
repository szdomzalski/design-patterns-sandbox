from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import pygame

from event_handling import EventPublisher, EventSubscriber, Timer
from game_logic import GameOfLifeRuleset
from singleton_subscriber_meta import SingletonSubscriberMeta
from ui import UI


class GameController(EventSubscriber, metaclass=SingletonSubscriberMeta):
    def __init__(self, timer: Timer, ui: UI, game_logic: GameOfLifeRuleset, initial_state: np.ndarray) -> None:
        '''
        Initialize the GameController.
        :param timer: The Timer object used to control the game timing.
        :param ui: The UI object responsible for rendering the game state.
        :param game_logic: The game logic (ruleset) to use (must implement GameOfLifeRuleset).
        :param initial_state: The initial game state as a numpy array.
        :return: None
        '''
        self.game_logic = game_logic
        self.board_state = initial_state
        self.ui_render_needed = False
        self.game_state: GameState = GameRunning()
        self.ui = ui
        self.ui.render(self.board_state)
        self.timer = timer
        self.timer.attach(self)

    def on_event(self, publisher: EventPublisher) -> None:
        '''
        Handle events from various publishers using pattern matching.
        :param publisher: The EventPublisher that triggered the event.
        :return: None
        '''
        match publisher:
            case Timer():
                self.board_state, self.ui_render_needed = self.game_state.handle_timer_tick(
                    self.game_logic, self.board_state)
            case _:
                pass

    def get_state(self) -> np.ndarray:
        '''
        Get the current game state.
        :return: The current game state as a numpy array.
        '''
        return self.board_state

    def run(self, timer: Timer) -> None:
        '''
        Run the main game loop, handling events and updating the UI.

        :param timer: The Timer object used to control the game timing.
        :return: None
        The loop continues running until a QUIT event is detected or the timer is stopped.
        Handles mouse button events to interact with UI buttons.
        Renders the UI when an update is needed.
        '''
        running = True
        with timer:
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
                                    timer.stop()
                                # Add more button actions here
                                break
                        # Only handle button clicks, do not break for non-button clicks
                if self.ui_render_needed:
                    self.ui.render(self.get_state())
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
