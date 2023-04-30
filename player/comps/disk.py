import os
from typing import Iterable


__all__ = (
    'Disk',
)


class Disk:
    """A `Disk` object stores and handles a sequenes of songs
    """
    def __init__(self, songs_list: Iterable[str]) -> None:
        """ The `self._playing_index` MUST always be aware of changes.
            This MUST EXPLICITLY return anything from self._songs ALWAYS
        """
        self._songs = songs_list
        self._playing_index = 0

    def __str__(self) -> str:
        return f"<Song('{self._songs[self._playing_index]}')>"

    def __repr__(self) -> str:
        return self._songs[self._playing_index]

    def __getitem__(self, i) -> str:
        return self._songs[i]

    def __contains__(self, __o) -> bool:
        return __o in self._songs

    def __len__(self) -> int:
        return len(self._songs)

    @property
    def song_index(self) -> int:
        return self._playing_index

    @property
    def song_mp3(self) -> str:
        return self[self._playing_index]

    @property
    def song(self) -> str:
        """Return the full path of the current song

        :return str:
        """
        return os.path.join('songs', self.song_mp3)

    def _move_song_index(self, direction: str) -> int:
        """When the `next` or `previous` song is out
        of list's range this function restarts
        self._playing_index accordingly
        instead of crashing or going to
        `-1` after `0`

        :param str direction: `up` for next / `down` for previous
        :return int: Properly handled self._playing_index
        """
        if direction == 'up':
            if self._playing_index + 1 > len(self):
                self._playing_index = 0
                return self._playing_index

        elif direction == 'down':
            if self._playing_index < 0:
                self._playing_index = len(self) - 1
                return self._playing_index

        return self._playing_index

    def next(self) -> str:
        """Go to next song

        :return str: Song at the next index of `self._songs`
        """
        self._playing_index += 1
        return self[self._move_song_index('up')]

    def prev(self) -> str:
        """Go to previous song

        :return str: Song at the previous index of `self._songs`
        """
        self._playing_index -= 1
        return self._songs[self._move_song_index('down')]

    def user_pick(self, index: int) -> str:
        """Track the song the user picked and point self._playing_index there

        :param index: The index of the song the user picked
        :type index: int
        :raises IndexError: In case the index is greater that the `Disk`
        :return: The song the user picked as `.mp3`
        :rtype: str
        """
        if index < 0:
            raise IndexError("Disk index cannot be negative")
        self._playing_index = index
        return self._songs[self._playing_index]

    def title(self) -> str:
        """Gives the title of the song without the extension
        ```
            >> self.song_mp3
            'Sjaak - Trompetisto (Official Music Video).mp3'
            >> self.title()
            'Sjaak - Trompetisto (Official Music Video)'
        ```

        :return: The title
        :rtype: str
        """
        reverse = self.song_mp3[::-1]
        return reverse[reverse.index('.') + 1:][::-1]