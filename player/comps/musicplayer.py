from .song import Song


class PlayerError(Exception): ...


class MusicPlayer:
    def __init__(self, song: Song) -> None:
        self.song = song
        self._is_playing = True
        self._volume = self.set_volume(100)
        self._timestamp = self.set_timestamp(0)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(Playing - {self.song.current_song} - {'Alive' if self._is_playing else 'Not alive'})>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(Playing - {self.song.current_song} - {'Alive' if self._is_playing else 'Not alive'})>"

    def __bool__(self):
        return self._is_playing

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def set_volume(self, volume: int) -> int:
        """Volume handler of the player

        :param int volume: The volume to set to
        :raises PlayerError: If the volume is more that 100 or less than 0
        :return int: Current volume
        """        
        if not 0 <= volume <= 100:
            raise PlayerError(f"Volume must remain between 0 - 100. It cannot be {volume}")
        self._volume = volume
        return self._volume

    def set_timestamp(self, timestamp: int):
        "TODO: Later see how to get the timestamp of each song"
        return timestamp

    def play(self) -> bool:
        """Reverse the _is_playing value

        :return bool: Current state of _is_playing
        """
        self._is_playing = not self._is_playing
        return self._is_playing
