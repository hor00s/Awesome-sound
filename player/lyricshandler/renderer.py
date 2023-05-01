import srt  # type: ignore
import datetime
from copy import copy
from typing import Union
from .constants import EXTENSION


__all__ = (
    'Renderer',
)


class Renderer:
    EXTENSION = EXTENSION

    def __init__(self, lyrics_file: str) -> None:
        self._lyrics_file = lyrics_file
        self._lyrics = tuple(srt.parse(self._set_lyrics()))
        self._index = 0

    def _set_lyrics(self) -> str:
        try:
            with open(self._lyrics_file, mode='r') as f:
                return f.read()
        except FileNotFoundError:
            return self._lyrics_file

    def get_line(self, current_timestamp: datetime.timedelta) -> Union[str, None]:
        # Not the most efficient way but it'll do for now
        for lyric in self._lyrics:
            if lyric.start <= current_timestamp < lyric.end:
                return str(lyric.content)
        return None

    def binary_lyrics_search(self, current_timestamp: datetime.timedelta) -> Union[str, None]:
        # This does the exact same as `lyrics.get_line` but it turns
        # out, this implementation of binary search is less efficient that
        # the linear solution
        lyrics = copy(self._lyrics)

        mid = lyrics[len(lyrics) // 2]

        while len(lyrics):
            mid = lyrics[len(lyrics) // 2]
            if len(lyrics) == 1 and (not mid.start <= current_timestamp < mid.end):
                # In case the value we're looking is missing
                return None

            elif mid.start <= current_timestamp < mid.end:
                return str(mid.content)
            elif mid.start <= current_timestamp:
                lyrics = lyrics[len(lyrics) // 2:]
                mid = lyrics[len(lyrics) // 2]
            elif mid.end > current_timestamp:
                lyrics = lyrics[:len(lyrics) // 2]
                mid = lyrics[len(lyrics) // 2]

        return None
