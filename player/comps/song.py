import os

class SingleToneSong(type):
    """Song class implements the SingleTon patter, which means that
    every time it's initiated it will return the same object,
    not a new one 
    """    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Song(metaclass=SingleToneSong):
    def __init__(self, songs_list: list) -> None:
        """ The `self._playing_index` MUST always be aware of changes.
            This MUST EXPLICITLY return anything from self._songs ALWAYS
        """        
        self._songs = songs_list
        self._playing_index = 0

    def __str__(self) -> str:
        return f"<Song('{self._songs[self._playing_index]}')>"

    def __repr__(self) -> str:
        return self._songs[self._playing_index]

    def __getitem__(self, i):
        return self._songs[i]

    def __contains__(self, __o):
        return __o in self._songs

    def __len__(self):
        return len(self._songs)

    @property
    def song_index(self):
        return self._playing_index

    @property
    def current_song(self) -> str:
        return self._songs[self._playing_index]

    @property
    def current_song_as_file(self) -> str:
        """Return the full path of the current song

        :return str:
        """        
        return os.path.join('songs', self.current_song)

    def _reset_song_index(self, direction: str) -> int:
        """When the `next` or `previous` song is out
        of list's range this function restarts
        self._playing_index accordingly
        instead of crashing or going to
        `-1` after `0`

        :param str direction: `up` for next / `down` for previous
        :return int: Properly handled self._playing_index
        """        
        if direction == 'up':
            if self._playing_index + 1 > len(self._songs):
                self._playing_index = 0
                return self._playing_index

        elif direction == 'down':
            if self._playing_index < 0:
                self._playing_index = len(self._songs) - 1
                return self._playing_index

        return self._playing_index

    def next(self) -> str:
        """Go to next song

        :return str: Song at the next index of `self._songs`
        """        
        self._playing_index += 1
        return self._songs[self._reset_song_index('up')]

    def prev(self) -> str:
        """Go to previous song

        :return str: Song at the previous index of `self._songs`
        """  
        self._playing_index -= 1
        return self._songs[self._reset_song_index('down')]

    def user_pick(self, index: int) -> str:
        if index < 0:
            raise IndexError("Songl list index cannot be negative")
        self._playing_index = index
        return self._songs[self._playing_index]

    def without_extension(self):
        reverse = self.current_song[::-1]
        # ext.sgsdgsd
        return reverse[reverse.index('.') + 1:][::-1]
