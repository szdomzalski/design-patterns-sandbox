from event_handling import EventSubscriber
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
        self.game_state = initial_state
        self.update_needed = False

    def on_event(self) -> None:
        '''
        Advance the simulation and set a flag for UI update.
        :return: None
        '''
        self.game_state = self.game_logic.next_generation(self.game_state)
        self.update_needed = True

    def get_state(self) -> np.ndarray:
        '''
        Get the current game state.
        :return: The current game state as a numpy array.
        '''
        return self.game_state
