from __future__ import annotations
from abc import ABC, abstractmethod
from event_handling import EventPublisher, EventSubscriber
from game_logic import GameOfLifeRuleset
import numpy as np


class GameController(EventSubscriber):
    def __init__(self, game_logic: GameOfLifeRuleset, initial_state: np.ndarray):
        '''
        Initialize the GameController.
        :param game_logic: The game logic (ruleset) to use (must implement GameOfLifeRuleset).
        :param initial_state: The initial game state as a numpy array.
        :return: None
        '''
        self.game_logic = game_logic
        self.board_state = initial_state
        self.update_needed = False
        self.game_state: GameState = GameStopped()

    def on_event(self, publisher: EventPublisher) -> None:
        '''
        Advance the simulation and set a flag for UI update.
        :param publisher: The EventPublisher that triggered the event.
        :return: None
        '''
        self.board_state = self.game_logic.next_generation(self.board_state)
        self.update_needed = True

    def get_state(self) -> np.ndarray:
        '''
        Get the current game state.
        :return: The current game state as a numpy array.
        '''
        return self.board_state


class GameState(ABC):
    '''
    Abstract base class (interface) for game operational state.
    '''


class GameStopped(GameState):
    '''
    Represents the stopped state of the game.
    This state indicates that the game is not running.
    '''


class GameRunning(GameState):
    '''
    Represents the running state of the game.
    This state indicates that the game is currently active and processing.
    '''
