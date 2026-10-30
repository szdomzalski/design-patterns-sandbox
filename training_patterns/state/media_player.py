from __future__ import annotations
from abc import ABC, abstractmethod


class PlayerState(ABC):
    '''Abstract base class for media player states.'''

    @abstractmethod
    def play(self, player: MediaPlayer) -> None:
        '''
        Play the media.
        :param player: The media player instance.
        :return: None
        '''
        pass

    @abstractmethod
    def pause(self, player: MediaPlayer) -> None:
        '''
        Pause the media.
        :param player: The media player instance.
        :return: None
        '''
        pass

    @abstractmethod
    def stop(self, player: MediaPlayer) -> None:
        '''
        Stop the media.
        :param player: The media player instance.
        :return: None
        '''
        pass


class PlayingState(PlayerState):
    '''Concrete state class for playing media.'''

    def play(self, player: MediaPlayer) -> None:
        '''
        Already playing, no action needed.
        :param player: The media player instance.
        :return: None
        '''
        print("Media is already playing.")

    def pause(self, player: MediaPlayer) -> None:
        '''
        Pause the media and change state to paused.
        :param player: The media player instance.
        :return: None
        '''
        print("Pausing media.")
        player.set_state(PausedState())

    def stop(self, player: MediaPlayer) -> None:
        '''
        Stop the media and change state to stopped.
        :param player: The media player instance.
        :return: None
        '''
        print("Stopping media.")
        player.set_state(StoppedState())


class PausedState(PlayerState):
    '''Concrete state class for paused media.'''

    def play(self, player: MediaPlayer) -> None:
        '''
        Resume playing the media and change state to playing.
        :param player: The media player instance.
        :return: None
        '''
        print("Resuming media.")
        player.set_state(PlayingState())

    def pause(self, player: MediaPlayer) -> None:
        '''
        Already paused, no action needed.
        :param player: The media player instance.
        :return: None
        '''
        print("Media is already paused.")

    def stop(self, player: MediaPlayer) -> None:
        '''
        Stop the media and change state to stopped.
        :param player: The media player instance.
        :return: None
        '''
        print("Stopping media from paused state.")
        player.set_state(StoppedState())


class StoppedState(PlayerState):
    '''Concrete state class for stopped media.'''

    def play(self, player: MediaPlayer) -> None:
        '''
        Start playing the media and change state to playing.
        :param player: The media player instance.
        :return: None
        '''
        print("Starting media playback.")
        player.set_state(PlayingState())

    def pause(self, player: MediaPlayer) -> None:
        '''
        Cannot pause when stopped, no action needed.
        :param player: The media player instance.
        :return: None
        '''
        print("Cannot pause, media is stopped.")

    def stop(self, player: MediaPlayer) -> None:
        '''
        Already stopped, no action needed.
        :param player: The media player instance.
        :return: None
        '''
        print("Media is already stopped.")


class MediaPlayer:
    '''Media player class that uses the state pattern.'''

    def __init__(self) -> None:
        '''Initialize the media player with a default state.'''
        self.__state: PlayerState = StoppedState()

    def set_state(self, state: PlayerState) -> None:
        '''
        Set the current state of the media player.
        :param state: The new state to set.
        :return: None
        '''
        self.__state = state

    def play(self) -> None:
        '''Play the media using the current state.'''
        self.__state.play(self)

    def pause(self) -> None:
        '''Pause the media using the current state.'''
        self.__state.pause(self)

    def stop(self) -> None:
        '''Stop the media using the current state.'''
        self.__state.stop(self)


if __name__ == "__main__":
    # Example usage of the MediaPlayer with state transitions
    player = MediaPlayer()

    player.play()  # Start playing
    player.pause()  # Pause the media
    player.play()  # Resume playing
    player.stop()  # Stop the media
    player.pause()  # Attempt to pause when stopped
    player.play()  # Start playing again
    player.stop()  # Stop the media again
    player.stop()  # Attempt to stop when already stopped
    player.play()
    player.play()
    player.pause()
    player.pause()
