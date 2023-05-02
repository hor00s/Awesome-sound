from comps.disk import Disk
from actions import config

__all__ = (
    'PlayerError',
    'MusicPlayer',
)


class PlayerError(Exception):
    pass


class MusicPlayer:
    def __init__(self, disk: Disk) -> None:
        self.disk = disk
        self._is_muted = config.get('is_muted')
        self._is_playing = True
        self._volume = self.set_volume()

    def __str__(self) -> str:
        state = 'Alive' if self._is_playing else 'Not alive'
        return f"<{self.__class__.__name__}(Playing - {self.disk.song_mp3} - {state})>"

    def __repr__(self) -> str:
        return str(self)

    def __bool__(self) -> bool:
        return self._is_playing

    @property
    def is_muted(self):
        return self._is_muted

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def mute(self):
        config.edit('is_muted', True)
        self._is_muted = config.get('is_muted')

    def unmute(self):
        config.edit('is_muted', False)
        self._is_muted = config.get('is_muted')

    def set_volume(self) -> int:
        """Volume handler of the player

        :param int volume: The volume to set to
        :raises PlayerError: If the volume is more that 100 or less than 0
        :return int: Current volume
        """
        volume = config.get('volume')
        if not 0 <= volume <= 100:
            raise PlayerError(f"Volume must remain between 0 - 100. It cannot be {volume}")

        self._volume = volume

        return self._volume

    def playing(self) -> bool:
        """Reverse the _is_playing value

        :return bool: Current state of _is_playing
        """
        self._is_playing = not self._is_playing
        return self._is_playing
