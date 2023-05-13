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
        """
        :return: `0 <= x <= 100`
        :rtype: int
        """
        return self._volume

    @property
    def is_playing(self) -> bool:
        """
        :return: `True` if the player is playing, `False` if the player is paused
        :rtype: bool
        """
        return self._is_playing

    def change_disk(self, new_disk: Disk, deletetion: bool = False) -> None:
        """Change the disk that is inserted in the `MusicPlayer`

        :param new_disk: A new disk object
        :type new_disk: Disk
        :param deletetion: Wheather a song was removed, defaults to False
        :type deletetion: bool, optional
        :raises PlayerError: If the `new_disk` is anything other that a `Disk` object
        """
        if not isinstance(new_disk, Disk):
            raise PlayerError(f"Player's disk cannot be of type -{type(new_disk)}-")
        current_playing = self.disk.song_mp3
        self.disk = new_disk

        if not deletetion:
            self.disk.user_pick(self.disk.full_song_list.index(current_playing))
        elif deletetion:
            self.disk.next()

    def mute(self) -> None:
        """Set the `MusicPlayer`'s `self._is_muted` state to `True`
        indicating the the `MusicPlayer` is muted
        """
        self._is_muted = True

    def unmute(self) -> None:
        """Set the `MusicPlayer`'s `self._is_muted` state to `False`
        indicating the the `MusicPlayer` is not muted
        """
        self._is_muted = False

    def set_volume(self, volume: int) -> int:
        """Volume handler of the player

        :param int volume: The volume to set to
        :raises PlayerError: If `volume` is not `0 <= volume <= 100`
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
