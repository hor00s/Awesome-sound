from comps.disk import Disk


__all__ = (
    'PlayerError',
    'MusicPlayer',
)


class PlayerError(Exception):
    pass


class MusicPlayer:
    def __init__(self, disk: Disk, is_muted: bool, volume: int) -> None:
        self.disk = disk
        self._is_muted = is_muted
        self._is_playing = True
        self._volume = volume

    def __str__(self) -> str:
        state = 'Alive' if self._is_playing else 'Not alive'
        return f"<{self.__class__.__name__}(Playing - {self.disk.song_mp3} - {state})>"

    def __repr__(self) -> str:
        return str(self)

    def __bool__(self) -> bool:
        return self._is_playing

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def change_disk(self, new_disk: Disk, deletetion: bool = False) -> None:
        if not isinstance(new_disk, Disk):
            raise PlayerError(f"Player's disk cannot be of type -{type(new_disk)}-")
        current_playing = self.disk.song_mp3
        self.disk = new_disk

        if not deletetion:
            self.disk.user_pick(self.disk.song_list.index(current_playing))
        elif deletetion:
            self.disk.next()

    def mute(self) -> None:
        self._is_muted = True

    def unmute(self) -> None:
        self._is_muted = False

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

    def playing(self) -> bool:
        """Reverse the _is_playing value

        :return bool: Current state of _is_playing
        """
        self._is_playing = not self._is_playing
        return self._is_playing
