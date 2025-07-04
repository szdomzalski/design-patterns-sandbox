from abc import ABC, abstractmethod
import numpy as np

class GameOfLifeRuleset(ABC):
    '''
    Abstract base class for Game of Life rulesets.
    This class defines the interface for calculating the next generation of the game state.
    Concrete rulesets should inherit from this class and implement the next_generation method.
    '''
    @abstractmethod
    def next_generation(self, state: np.ndarray) -> np.ndarray:
        '''
        Calculate the next generation of the game state.
        :param state: Current game state as a 2D numpy array.
        :return: Next generation as a 2D numpy array.
        '''
        pass

class ClassicGameOfLife(GameOfLifeRuleset):
    '''
    Classic Game of Life ruleset implementation.
    Implements Conway's original rules for cell survival and birth.
    '''
    def next_generation(self, state: np.ndarray) -> np.ndarray:
        '''
        Calculate the next generation of the game state using Conway's rules.
        :param state: Current game state as a 2D numpy array.
        :return: Next generation as a 2D numpy array.
        '''
        n_cells_x, n_cells_y = state.shape
        new_state = np.copy(state)
        for y in range(n_cells_y):
            for x in range(n_cells_x):
                n_neighbors = state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                              state[(x)     % n_cells_x, (y - 1) % n_cells_y] + \
                              state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                              state[(x - 1) % n_cells_x, (y)     % n_cells_y] + \
                              state[(x + 1) % n_cells_x, (y)     % n_cells_y] + \
                              state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                              state[(x)     % n_cells_x, (y + 1) % n_cells_y] + \
                              state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]
                if state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                    new_state[x, y] = 0
                elif state[x, y] == 0 and n_neighbors == 3:
                    new_state[x, y] = 1
        return new_state
