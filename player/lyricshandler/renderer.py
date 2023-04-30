import srt
import datetime
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

    def _set_lyrics(self):
        try:
            with open(self._lyrics_file, mode='r') as f:
                return f.read()
        except FileNotFoundError:
            return self._lyrics_file

    def get_line(self, current_timestamp: datetime.timedelta):
        # Not the most efficient way but it'll do for now
        for lyric in self._lyrics:
            if lyric.start <= current_timestamp < lyric.end:
                return lyric.content
        return None
